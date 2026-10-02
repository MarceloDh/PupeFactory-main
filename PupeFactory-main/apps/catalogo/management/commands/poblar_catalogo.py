from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.catalogo.models import Categoria, Marca, Producto

# ==============================================================================
# COMANDO PARA POBLAR CATÁLOGO CON HARDWARE REAL Y STOCK REALISTA
# ==============================================================================
# Configura categorías, marcas y amplio catálogo de componentes de PC
# cumpliendo los requerimientos de la Rúbrica EVA-2 y demostración de stock.
# ==============================================================================

class Command(BaseCommand):
    help = 'Puebla el catálogo con hardware real, variedad de marcas y stock realista.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Operación bloqueada: Solo permitido en modo desarrollo (DEBUG=True).")

        # 1. Categorías Ampliadas
        categorias_data = [
            ('Procesadores', 'procesadores', 'CPUs Intel y AMD para gaming, creación de contenido y multitarea.'),
            ('Tarjetas de Video', 'tarjetas-video', 'GPUs NVIDIA GeForce RTX y AMD Radeon de última generación.'),
            ('Memorias RAM', 'memorias-ram', 'Módulos DDR4 y DDR5 de alto rendimiento y baja latencia.'),
            ('Almacenamiento', 'almacenamiento', 'Unidades SSD NVMe M.2 ultra veloces y discos mecánicos HDD.'),
            ('Placas Madre', 'placas-madre', 'Motherboards para plataformas Socket AM5, AM4 y LGA1700.'),
            ('Fuentes de Poder', 'fuentes-poder', 'PSUs con certificación 80 Plus Gold y Bronze para setups estables.'),
            ('Gabinetes', 'gabinetes', 'Gabinetes con flujo de aire optimizado, vidrio templado y RGB.'),
            ('Refrigeración', 'refrigeracion', 'Coolers por aire, refrigeraciones líquidas AIO y ventiladores PWM.'),
        ]
        cat_objs = {}
        for nombre, slug, desc in categorias_data:
            cat, _ = Categoria.objects.get_or_create(slug=slug, defaults={'nombre': nombre, 'descripcion': desc})
            cat_objs[slug] = cat

        # 2. Marcas del Ecosistema PC
        marcas_data = [
            ('AMD', 'amd'),
            ('NVIDIA', 'nvidia'),
            ('Intel', 'intel'),
            ('ASUS', 'asus'),
            ('MSI', 'msi'),
            ('Gigabyte', 'gigabyte'),
            ('Corsair', 'corsair'),
            ('Kingston', 'kingston'),
            ('Western Digital', 'western-digital'),
            ('Seasonic', 'seasonic'),
            ('NZXT', 'nzxt'),
            ('DeepCool', 'deepcool'),
        ]
        marca_objs = {}
        for nombre, slug in marcas_data:
            m, _ = Marca.objects.get_or_create(slug=slug, defaults={'nombre': nombre})
            marca_objs[slug] = m

        # 3. Productos Reales con Stock Diferenciado
        productos_data = [
            # ======================== TARJETAS DE VIDEO ========================
            {
                'nombre': 'ASUS ROG Strix GeForce RTX 4090 24GB GDDR6X',
                'sku': 'GPU-ASUS-RTX4090-24G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['asus'],
                'descripcion': 'El rendimiento gráfico definitivo. 16384 núcleos CUDA, 24GB GDDR6X y disipador masivo de 3.5 slots.',
                'precio': Decimal('2199990.00'),
                'stock': 2,  # Producto premium de stock muy escaso
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/6499a224-fa77-4c48-84dc-6644f1c998f4/v1/img/kv/pd.png'
            },
            {
                'nombre': 'MSI GeForce RTX 4080 Super Gaming X Slim 16GB',
                'sku': 'GPU-MSI-RTX4080S-16G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['msi'],
                'descripcion': 'Potencia extrema para 4K con tecnología DLSS 3, trazado de rayos completo y formato Slim.',
                'precio': Decimal('1299990.00'),
                'stock': 3,
                'activo': True,
                'imagen_url': 'https://storage-asset.msi.com/global/picture/image/feature/vga/NVIDIA/RTX-4080-SUPER-GAMING-X-SLIM-16G/images/kv-pd.png'
            },
            {
                'nombre': 'ASUS TUF Gaming GeForce RTX 4070 Super 12GB',
                'sku': 'GPU-ASUS-RTX4070S-12G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['asus'],
                'descripcion': 'Excelente balance para 1440p competitivo con componentes militares y ventiladores axial-tech.',
                'precio': Decimal('749990.00'),
                'stock': 5,
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/19fb5434-2e21-4fba-8d5f-2ffca128a305/v1/img/kv/pd.png'
            },
            {
                'nombre': 'Gigabyte GeForce RTX 4070 Windforce OC 12GB',
                'sku': 'GPU-GB-RTX4070-12G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['gigabyte'],
                'descripcion': 'Eficiencia térmica con triple ventilador Windforce y placa posterior de protección metálica.',
                'precio': Decimal('649990.00'),
                'stock': 6,
                'activo': True,
                'imagen_url': 'https://static.gigabyte.com/StaticFile/Image/Global/07eb02f74158e2bf65609653a9fe39a4/Product/34407/png/1000'
            },
            {
                'nombre': 'MSI GeForce RTX 4060 Ti Ventus 2X Black 16GB',
                'sku': 'GPU-MSI-RTX4060TI-16G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['msi'],
                'descripcion': '16GB de VRAM ideales para creación, edición de video y gaming a 1080p y 1440p con DLSS 3.',
                'precio': Decimal('499990.00'),
                'stock': 9,
                'activo': True,
                'imagen_url': 'https://storage-asset.msi.com/global/picture/image/feature/vga/NVIDIA/RTX-4060-Ti-VENTUS-2X-BLACK-16G/images/kv-pd.png'
            },
            {
                'nombre': 'ASUS Dual GeForce RTX 4060 OC 8GB',
                'sku': 'GPU-ASUS-RTX4060-8G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['asus'],
                'descripcion': 'Rendimiento compacto para cajas mATX y gaming a 1080p a más de 100 FPS con trazado de rayos.',
                'precio': Decimal('339990.00'),
                'stock': 12,
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/6499a224-fa77-4c48-84dc-6644f1c998f4/v1/img/kv/pd.png'
            },
            {
                'nombre': 'Sapphire Nitro+ AMD Radeon RX 7900 XTX 24GB',
                'sku': 'GPU-AMD-7900XTX-24G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['amd'],
                'descripcion': 'Arquitectura RDNA 3 insignia con 24GB GDDR6, Infinity Cache y DisplayPort 2.1.',
                'precio': Decimal('1149990.00'),
                'stock': 2,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/graphics/radeon/2505503-radeon-rx-7900-xtx.jpg'
            },
            {
                'nombre': 'ASUS TUF Gaming Radeon RX 7800 XT 16GB',
                'sku': 'GPU-AMD-7800XT-16G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['asus'],
                'descripcion': 'Dominio total para gaming en 1440p nativo con 16GB de memoria VRAM de alta velocidad.',
                'precio': Decimal('599990.00'),
                'stock': 5,
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/19fb5434-2e21-4fba-8d5f-2ffca128a305/v1/img/kv/pd.png'
            },
            {
                'nombre': 'Gigabyte Radeon RX 7700 XT Gaming OC 12GB',
                'sku': 'GPU-AMD-7700XT-12G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['gigabyte'],
                'descripcion': 'Rendimiento sólido con 12GB GDDR6, AMD HYPR-RX y arquitectura RDNA 3 optimizada.',
                'precio': Decimal('479990.00'),
                'stock': 7,
                'activo': True,
                'imagen_url': 'https://static.gigabyte.com/StaticFile/Image/Global/07eb02f74158e2bf65609653a9fe39a4/Product/34407/png/1000'
            },
            {
                'nombre': 'MSI Radeon RX 7600 Mech 2X Classic 8GB',
                'sku': 'GPU-AMD-7600-8G',
                'categoria': cat_objs['tarjetas-video'],
                'marca': marca_objs['msi'],
                'descripcion': 'GPU accesible con gran desempeño en juegos eSports a 1080p con codificación AV1.',
                'precio': Decimal('289990.00'),
                'stock': 10,
                'activo': True,
                'imagen_url': 'https://storage-asset.msi.com/global/picture/image/feature/vga/AMD/RX-7600-MECH-2X-CLASSIC-8G/images/kv-pd.png'
            },

            # ======================== PROCESADORES ========================
            {
                'nombre': 'Intel Core i9 14900K 24-Core 6.0 GHz LGA1700',
                'sku': 'CPU-INTEL-14900K',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['intel'],
                'descripcion': '24 núcleos (8P + 16E) y 32 hilos con frecuencia Turbo de hasta 6.0 GHz para creadores y entusiastas.',
                'precio': Decimal('629990.00'),
                'stock': 3,
                'activo': True,
                'imagen_url': 'https://www.intel.la/content/dam/www/central-libraries/us/en/images/2023-09/raptor-lake-refresh-i9-boxed-badge-rwd.png.rendition.intel.cq5dam.thumbnail.319.319.png'
            },
            {
                'nombre': 'Intel Core i7 14700K 20-Core 5.6 GHz LGA1700',
                'sku': 'CPU-INTEL-14700K',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['intel'],
                'descripcion': '20 núcleos (8P + 12E) y 28 hilos. Aumento notable de caché para gaming y renderizado pesado.',
                'precio': Decimal('449990.00'),
                'stock': 8,
                'activo': True,
                'imagen_url': 'https://www.intel.la/content/dam/www/central-libraries/us/en/images/2023-09/raptor-lake-refresh-i7-boxed-badge-rwd.png.rendition.intel.cq5dam.thumbnail.319.319.png'
            },
            {
                'nombre': 'Intel Core i5 14600K 14-Core 5.3 GHz LGA1700',
                'sku': 'CPU-INTEL-14600K',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['intel'],
                'descripcion': 'El procesador balanceado de referencia. 14 núcleos (6P + 8E) y 20 hilos desbloqueado para overclocking.',
                'precio': Decimal('339990.00'),
                'stock': 14,
                'activo': True,
                'imagen_url': 'https://www.intel.la/content/dam/www/central-libraries/us/en/images/2023-09/raptor-lake-refresh-i5-boxed-badge-rwd.png.rendition.intel.cq5dam.thumbnail.319.319.png'
            },
            {
                'nombre': 'Intel Core i5 14400F 10-Core 4.7 GHz LGA1700',
                'sku': 'CPU-INTEL-14400F',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['intel'],
                'descripcion': '10 núcleos y 16 hilos. Gran eficiencia para presupuestos equilibrados requiriendo tarjeta gráfica dedicada.',
                'precio': Decimal('219990.00'),
                'stock': 22,
                'activo': True,
                'imagen_url': 'https://www.intel.la/content/dam/www/central-libraries/us/en/images/2023-09/raptor-lake-refresh-i5-boxed-badge-rwd.png.rendition.intel.cq5dam.thumbnail.319.319.png'
            },
            {
                'nombre': 'Intel Core i3 14100 4-Core 4.7 GHz LGA1700',
                'sku': 'CPU-INTEL-14100',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['intel'],
                'descripcion': '4 núcleos de alto rendimiento y 8 hilos con gráficos integrados Intel UHD 730.',
                'precio': Decimal('129990.00'),
                'stock': 15,
                'activo': True,
                'imagen_url': 'https://www.intel.la/content/dam/www/central-libraries/us/en/images/2023-09/raptor-lake-refresh-i3-boxed-badge-rwd.png.rendition.intel.cq5dam.thumbnail.319.319.png'
            },
            {
                'nombre': 'AMD Ryzen 9 7950X 16-Core 5.7 GHz Socket AM5',
                'sku': 'CPU-AMD-7950X',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['amd'],
                'descripcion': '16 núcleos y 32 hilos en arquitectura Zen 4. Máxima potencia para compilar, renderizar y simular.',
                'precio': Decimal('589990.00'),
                'stock': 3,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2505503-ryzen-9-7950x-front.jpg'
            },
            {
                'nombre': 'AMD Ryzen 9 7900 12-Core 5.4 GHz Socket AM5',
                'sku': 'CPU-AMD-7900',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['amd'],
                'descripcion': '12 núcleos y 24 hilos con TDP eficiente de 65W e incluye cooler Wraith Prism RGB.',
                'precio': Decimal('419990.00'),
                'stock': 5,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2505503-ryzen-9-7900-front.jpg'
            },
            {
                'nombre': 'AMD Ryzen 7 7800X3D 8-Core con 3D V-Cache AM5',
                'sku': 'CPU-AMD-7800X3D',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['amd'],
                'descripcion': 'El procesador gaming número 1 del mundo con 96MB de L3 Caché para tasas de cuadros ultra estables.',
                'precio': Decimal('429990.00'),
                'stock': 6,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2505503-ryzen-7-7800x3d-front.jpg'
            },
            {
                'nombre': 'AMD Ryzen 5 7600 6-Core 5.1 GHz Socket AM5',
                'sku': 'CPU-AMD-7600',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['amd'],
                'descripcion': 'Entrada directa a la plataforma AM5 y memorias DDR5 con 6 núcleos y 12 hilos rápidos.',
                'precio': Decimal('219990.00'),
                'stock': 15,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2505503-ryzen-5-7600-front.jpg'
            },
            {
                'nombre': 'AMD Ryzen 5 5600 6-Core 4.4 GHz Socket AM4',
                'sku': 'CPU-AMD-5600',
                'categoria': cat_objs['procesadores'],
                'marca': marca_objs['amd'],
                'descripcion': 'El rey del valor precio/rendimiento para la plataforma AM4 con memoria DDR4.',
                'precio': Decimal('129990.00'),
                'stock': 18,
                'activo': True,
                'imagen_url': 'https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2505503-ryzen-5-5600-front.jpg'
            },

            # ======================== PLACAS MADRE ========================
            {
                'nombre': 'ASUS ROG Maximus Z790 Dark Hero WiFi',
                'sku': 'MB-ASUS-Z790-MAX',
                'categoria': cat_objs['placas-madre'],
                'marca': marca_objs['asus'],
                'descripcion': 'Placa madre premium LGA1700 con 20+1 fases de poder, PCIe 5.0 M.2 y conectividad WiFi 7.',
                'precio': Decimal('699990.00'),
                'stock': 2,
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/7f358aac-d2d6-4dd0-8fba-dea85469a22e/V1/img/kv-main.png'
            },
            {
                'nombre': 'MSI MAG B650 Tomahawk WiFi AM5',
                'sku': 'MB-MSI-B650-TOMA',
                'categoria': cat_objs['placas-madre'],
                'marca': marca_objs['msi'],
                'descripcion': 'VRM robusto de 14+2+1 fases, soporte DDR5, triple ranura M.2 Shield Frozr y WiFi 6E.',
                'precio': Decimal('229990.00'),
                'stock': 8,
                'activo': True,
                'imagen_url': 'https://storage-asset.msi.com/global/picture/image/feature/mb/B650/MAG-B650-TOMAHAWK-WIFI/images/kv-pd.png'
            },
            {
                'nombre': 'Gigabyte B760M AORUS Elite AX DDR5',
                'sku': 'MB-GB-B760M-AORUS',
                'categoria': cat_objs['placas-madre'],
                'marca': marca_objs['gigabyte'],
                'descripcion': 'Formato microATX para procesadores Intel de 14va generación con WiFi 6E y doble M.2 térmico.',
                'precio': Decimal('179990.00'),
                'stock': 11,
                'activo': True,
                'imagen_url': 'https://static.gigabyte.com/StaticFile/Image/Global/07eb02f74158e2bf65609653a9fe39a4/Product/34407/png/1000'
            },
            {
                'nombre': 'ASUS TUF Gaming B650-PLUS WIFI AM5',
                'sku': 'MB-ASUS-TUF-B650P',
                'categoria': cat_objs['placas-madre'],
                'marca': marca_objs['asus'],
                'descripcion': 'Socket AM5 con diseño militar durable, soporte PCIe 5.0 M.2 y cancelación de ruido por IA bidireccional.',
                'precio': Decimal('199990.00'),
                'stock': 6,
                'activo': True,
                'imagen_url': 'https://dlcdnwebimgs.asus.com/files/media/7f358aac-d2d6-4dd0-8fba-dea85469a22e/V1/img/kv-main.png'
            },

            # ======================== MEMORIAS RAM ========================
            {
                'nombre': 'Corsair Vengeance RGB DDR5 32GB (2x16GB) 6000MHz CL30',
                'sku': 'RAM-COR-DDR5-32G6000',
                'categoria': cat_objs['memorias-ram'],
                'marca': marca_objs['corsair'],
                'descripcion': 'Optimizado para AMD EXPO e Intel XMP con iluminación RGB dinámica de diez zonas direccionables.',
                'precio': Decimal('134990.00'),
                'stock': 25,
                'activo': True,
                'imagen_url': 'https://assets.corsair.com/image/upload/c_pad,q_auto,h_1024,w_1024,f_auto/products/Memory/vengeance-rgb-ddr5-blk-config/Gallery/2up/VENGEANCE_RGB_DDR5_BLK_01.webp'
            },
            {
                'nombre': 'Kingston Fury Beast DDR4 16GB (2x8GB) 3200MHz',
                'sku': 'RAM-KIN-DDR4-16G3200',
                'categoria': cat_objs['memorias-ram'],
                'marca': marca_objs['kingston'],
                'descripcion': 'Kit de doble canal con disipador de calor de bajo perfil para máxima compatibilidad con disipadores.',
                'precio': Decimal('42990.00'),
                'stock': 30,
                'activo': True,
                'imagen_url': 'https://media.kingston.com/kingston/press/ktc-press-fury-renegade-beast-ddr4-lg.jpg'
            },
            {
                'nombre': 'Corsair Dominator Titanium RGB DDR5 64GB (2x32GB) 6400MHz',
                'sku': 'RAM-COR-DDR5-64G6400',
                'categoria': cat_objs['memorias-ram'],
                'marca': marca_objs['corsair'],
                'descripcion': 'Memoria DDR5 de grado audiófilo/entusiasta con chips Samsung seleccionados a mano.',
                'precio': Decimal('289990.00'),
                'stock': 4,
                'activo': True,
                'imagen_url': 'https://assets.corsair.com/image/upload/c_pad,q_auto,h_1024,w_1024,f_auto/products/Memory/dominator-titanium-ddr5-blk-config/Gallery/DOMINATOR_TITANIUM_01.webp'
            },
            {
                'nombre': 'Kingston ValueRAM DDR4 8GB 2666MHz (Edición Básica)',
                'sku': 'RAM-KIN-DDR4-8G2666',
                'categoria': cat_objs['memorias-ram'],
                'marca': marca_objs['kingston'],
                'descripcion': 'Módulo individual para oficinas y equipos compactos. Temporalmente sin stock de fábrica.',
                'precio': Decimal('24990.00'),
                'stock': 0,  # Demostración explícita de producto agotado
                'activo': True,
                'imagen_url': 'https://media.kingston.com/kingston/press/ktc-press-fury-renegade-beast-ddr4-lg.jpg'
            },

            # ======================== ALMACENAMIENTO ========================
            {
                'nombre': 'WD Black SN850X 1TB NVMe PCIe 4.0 M.2',
                'sku': 'SSD-WD-SN850X-1TB',
                'categoria': cat_objs['almacenamiento'],
                'marca': marca_objs['western-digital'],
                'descripcion': 'Velocidades de hasta 7300 MB/s de lectura. Uno de los SSDs más populares y recomendados del mercado.',
                'precio': Decimal('99990.00'),
                'stock': 40,  # Producto masivo y común con gran stock
                'activo': True,
                'imagen_url': 'https://www.westerndigital.com/content/dam/store/en-us/assets/products/internal-storage/wd-black-sn850x-nvme-ssd/gallery/wd-black-sn850x-nvme-ssd-1tb.png'
            },
            {
                'nombre': 'Kingston KC3000 2TB NVMe PCIe 4.0 M.2',
                'sku': 'SSD-KIN-KC3000-2TB',
                'categoria': cat_objs['almacenamiento'],
                'marca': marca_objs['kingston'],
                'descripcion': 'Rendimiento supremo con controlador Phison E18 y disipador de aluminio con grafeno.',
                'precio': Decimal('164990.00'),
                'stock': 16,
                'activo': True,
                'imagen_url': 'https://tpucdn.com/ssd-specs/images/d/260-front.jpg'
            },
            {
                'nombre': 'Western Digital Blue 2TB 7200 RPM HDD 3.5"',
                'sku': 'HDD-WD-BLUE-2TB',
                'categoria': cat_objs['almacenamiento'],
                'marca': marca_objs['western-digital'],
                'descripcion': 'Almacenamiento masivo confiable para respaldos, fotos y juegos secundarios.',
                'precio': Decimal('59990.00'),
                'stock': 25,
                'activo': True,
                'imagen_url': 'https://www.westerndigital.com/content/dam/store/en-us/assets/products/internal-storage/wd-blue-desktop-sata-hdd/gallery/wd-blue-desktop-sata-hdd-2tb.png'
            },

            # ======================== FUENTES DE PODER ========================
            {
                'nombre': 'Corsair RM1000x 1000W 80 Plus Gold Full Modular',
                'sku': 'PSU-COR-RM1000X',
                'categoria': cat_objs['fuentes-poder'],
                'marca': marca_objs['corsair'],
                'descripcion': 'Condensadores 100% japoneses a 105°C, soporte ATX 3.0 con conector nativo PCIe 5.0 12VHPWR.',
                'precio': Decimal('199990.00'),
                'stock': 5,
                'activo': True,
                'imagen_url': 'https://assets.corsair.com/image/upload/c_pad,q_auto,h_1024,w_1024,f_auto/products/Power-Supply-Units/rmx-series-config/Gallery/RM1000x_01.webp'
            },
            {
                'nombre': 'Seasonic Focus GX-850 850W 80 Plus Gold',
                'sku': 'PSU-SEA-GX850',
                'categoria': cat_objs['fuentes-poder'],
                'marca': marca_objs['seasonic'],
                'descripcion': 'Control inteligente de ventilador híbrido silencioso con 10 años de garantía del fabricante.',
                'precio': Decimal('149990.00'),
                'stock': 10,
                'activo': True,
                'imagen_url': 'https://seasonic.com/wp-content/uploads/2023/07/FOCUS-GX-ATX3-Photo-01.png'
            },
            {
                'nombre': 'MSI MAG A650BN 650W 80 Plus Bronze',
                'sku': 'PSU-MSI-A650BN',
                'categoria': cat_objs['fuentes-poder'],
                'marca': marca_objs['msi'],
                'descripcion': 'Fuente confiable para configuraciones de gama media con protecciones OCP, OVP, OPP y SCP.',
                'precio': Decimal('59990.00'),
                'stock': 18,
                'activo': True,
                'imagen_url': 'https://storage-asset.msi.com/global/picture/image/feature/power/MAG-A650BN/images/kv-pd.png'
            },

            # ======================== GABINETES ========================
            {
                'nombre': 'NZXT H5 Flow RGB Black Mid-Tower con 2x F140 RGB',
                'sku': 'CASE-NZXT-H5F-BK',
                'categoria': cat_objs['gabinetes'],
                'marca': marca_objs['nzxt'],
                'descripcion': 'Panel frontal perforado para flujo de aire máximo y ventilador inferior dedicado a la GPU.',
                'precio': Decimal('109990.00'),
                'stock': 7,
                'activo': True,
                'imagen_url': 'https://nzxt.com/assets/cms/34299/1665476332-h5-flow-rgb-black-primary.png'
            },
            {
                'nombre': 'Corsair 4000D Airflow Vidrio Templado Black',
                'sku': 'CASE-COR-4000D-AIR',
                'categoria': cat_objs['gabinetes'],
                'marca': marca_objs['corsair'],
                'descripcion': 'Canal de gestión de cables RapidRoute y dos ventiladores AirGuide de 120mm incluidos.',
                'precio': Decimal('99990.00'),
                'stock': 9,
                'activo': True,
                'imagen_url': 'https://assets.corsair.com/image/upload/c_pad,q_auto,h_1024,w_1024,f_auto/products/Cases/4000d-airflow-config/Gallery/4000D_AIRFLOW_BLACK_01.webp'
            },

            # ======================== REFRIGERACIÓN Y VENTILADORES ========================
            {
                'nombre': 'NZXT Kraken 360 RGB AIO Liquid Cooler 360mm',
                'sku': 'COOL-NZXT-KR360',
                'categoria': cat_objs['refrigeracion'],
                'marca': marca_objs['nzxt'],
                'descripcion': 'Pantalla LCD cuadrada de 1.54 pulgadas para monitorear temperaturas de CPU y GPU en tiempo real.',
                'precio': Decimal('239990.00'),
                'stock': 4,
                'activo': True,
                'imagen_url': 'https://nzxt.com/assets/cms/34299/1681283626-kraken-360-rgb-black-primary.png'
            },
            {
                'nombre': 'DeepCool AK620 Digital Doble Torre con Display',
                'sku': 'COOL-DC-AK620D',
                'categoria': cat_objs['refrigeracion'],
                'marca': marca_objs['deepcool'],
                'descripcion': 'Disipador por aire de 260W TDP con pantalla digital que muestra estado y temperatura en tiempo real.',
                'precio': Decimal('79990.00'),
                'stock': 12,
                'activo': True,
                'imagen_url': 'https://www.deepcool.com/download/image/AK620_DIGITAL_01.png'
            },
            {
                'nombre': 'Corsair iCUE SP120 RGB Elite 120mm PWM (Pack x3)',
                'sku': 'FAN-COR-SP120-3PK',
                'categoria': cat_objs['refrigeracion'],
                'marca': marca_objs['corsair'],
                'descripcion': 'Pack de tres ventiladores PWM con 8 LEDs RGB direccionables por ventilador y controlador iCUE Lighting Node CORE.',
                'precio': Decimal('64990.00'),
                'stock': 20,
                'activo': True,
                'imagen_url': 'https://assets.corsair.com/image/upload/c_pad,q_auto,h_1024,w_1024,f_auto/products/Fans/sp-rgb-elite-fans/Gallery/SP120_RGB_ELITE_01.webp'
            },
        ]

        from .specs_data import IMAGE_CATEGORY_MAP, IMAGE_SPECIFIC_MAP, HARDWARE_SPECS

        count = 0
        for pdata in productos_data:
            sku = pdata['sku']
            cat_slug = pdata['categoria'].slug
            local_img = IMAGE_SPECIFIC_MAP.get(sku) or IMAGE_CATEGORY_MAP.get(cat_slug, 'productos/rtx4070.jpg')
            specs = HARDWARE_SPECS.get(sku, {})
            pdata['imagen'] = local_img
            pdata['especificaciones'] = specs
            p, created = Producto.objects.update_or_create(sku=sku, defaults=pdata)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] Catálogo enriquecido exitosamente con {count} productos de hardware, imágenes locales y especificaciones técnicas."))

