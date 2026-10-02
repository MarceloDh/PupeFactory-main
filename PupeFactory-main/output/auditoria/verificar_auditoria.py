"""Reproducciones de auditoría. Usa únicamente una base SQLite en memoria."""
import os
import sys
import json
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pupefactory.settings')
import django
from django.conf import settings
settings.DATABASES['default']['NAME'] = ':memory:'
settings.DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
django.setup()
from django.core.management import call_command
from django.test import Client, RequestFactory
from django.contrib import admin
from apps.usuarios.models import CustomUser
from apps.catalogo.models import Categoria, Marca, Producto
from apps.carro.services import CartService
from apps.ordenes.models import Orden, OrdenItem
from apps.ordenes.services import OrdenService
from apps.ordenes.admin import OrdenAdmin
from drf_spectacular.generators import SchemaGenerator

call_command('migrate', verbosity=0)
c = Categoria.objects.create(nombre='CPU', slug='cpu')
m = Marca.objects.create(nombre='AMD', slug='amd')
u = CustomUser.objects.create_user(username='auditoria', password='AuditPass123!')
a = CustomUser.objects.create_superuser(username='audit_admin', password='AuditPass123!', role='ADMINISTRADOR')
p = Producto.objects.create(nombre='Audit CPU', sku='AUDIT-CPU', categoria=c, marca=m, stock=10, precio=100)
results = {}

CartService.add_item(u, p.id, 2)
o = OrdenService.checkout(u)
p.refresh_from_db()
before = p.stock
o.estado = Orden.Estado.CANCELADO
req = RequestFactory().post('/admin/ordenes/orden/')
req.user = a
OrdenAdmin(Orden, admin.site).save_model(req, o, None, True)
p.refresh_from_db()
results['cancelacion_desde_admin'] = {'stock_antes': before, 'stock_despues': p.stock, 'esperado': 10, 'estado': Orden.objects.get(pk=o.pk).estado}

CartService.add_item(u, p.id, 1)
real_atomic = django.db.transaction.atomic
triggered = False
@contextmanager
def interleaved_atomic(*args, **kwargs):
    global triggered
    if not triggered:
        triggered = True
        # La petición exterior ya leyó los ítems. Otra petición compra y vacía el carro.
        OrdenService.checkout(u)
    with real_atomic(*args, **kwargs):
        yield
count_before = Orden.objects.count()
with patch('apps.ordenes.services.transaction.atomic', interleaved_atomic):
    OrdenService.checkout(u)
results['checkout_mismo_carro_intercalado'] = {'ordenes_creadas': Orden.objects.count() - count_before, 'esperado': 1, 'metodo': 'intercalado determinista; no son hilos ni bloqueo PostgreSQL'}

pending = Orden.objects.create(numero_orden='AUDIT-PENDIENTE', usuario=u)
OrdenItem.objects.create(orden=pending, producto=p, cantidad=1, precio_unitario=100)
p.activo = False
p.save()
OrdenService.cambiar_estado_orden(pending.id, 'PAGADO', a)
pending.refresh_from_db()
results['pago_pendiente_producto_inactivo'] = {'estado_obtenido': pending.estado, 'esperado': 'rechazo'}

p.activo = True
p.save()
for i in range(13):
    Producto.objects.create(nombre=f'Other {i}', sku=f'OTHER-{i}', categoria=c, marca=m, stock=5, precio=200+i)
client = Client()
web = client.get('/catalogo/')
page2 = client.get('/catalogo/?page=2')
results['catalogo_paginacion'] = {'productos_totales': Producto.objects.count(), 'tarjetas_pagina1': web.content.count(b'class="product-card"'), 'tarjetas_pagina2': page2.content.count(b'class="product-card"'), 'enlace_page_en_html': b'page=' in web.content}
results['busqueda_api'] = {'con_q': len(client.get('/api/productos/?q=Audit').json()), 'con_search': len(client.get('/api/productos/?search=Audit').json())}
results['filtro_precio_web'] = {'tarjetas_con_precio_min_10000': client.get('/catalogo/?precio_min=10000').content.count(b'class="product-card"'), 'esperado': 0}
client.force_login(u)
CartService.add_item(u, p.id, 1)
results['persistencia_logout'] = {'logout_status': client.post('/accounts/logout/').status_code}
client2 = Client()
client2.force_login(u)
results['persistencia_logout']['unidades_otra_sesion'] = client2.get('/api/carro/').json()['total_items']
try:
    schema = SchemaGenerator().get_schema(request=None, public=True)
    results['openapi_generacion'] = {'ok': True, 'rutas': len(schema['paths'])}
except Exception as e:
    results['openapi_generacion'] = {'ok': False, 'error': str(e)}
output = Path(__file__).with_name('resultados_reproducciones.json')
output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results, ensure_ascii=False, indent=2))
