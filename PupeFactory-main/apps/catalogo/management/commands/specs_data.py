"""
Diccionario estructurado de especificaciones técnicas y mapeo de imágenes reales
para el comando poblar_catalogo de PupeFactory.
"""

IMAGE_CATEGORY_MAP = {
    'tarjetas-video': 'productos/rtx4070.jpg',
    'procesadores': 'productos/ryzen7000.jpg',
    'placas-madre': 'productos/motherboard_am5.jpg',
    'memorias-ram': 'productos/ram_ddr5.jpg',
    'almacenamiento': 'productos/ssd_kc3000.jpg',
    'fuentes-poder': 'productos/psu_rm1000x.jpg',
    'gabinetes': 'productos/case_airflow.jpg',
    'refrigeracion': 'productos/cooler_kraken.jpg',
}

IMAGE_SPECIFIC_MAP = {
    'GPU-ASUS-RTX4090-24G': 'productos/rtx4090.jpg',
    'GPU-ASUS-RTX5070-16G': 'productos/rtx4090.jpg',
    'GPU-AMD-7900XTX-24G': 'productos/rx7900xtx.jpg',
    'GPU-AMD-7800XT-16G': 'productos/rx7900xtx.jpg',
    'GPU-AMD-7700XT-12G': 'productos/rx7900xtx.jpg',
    'GPU-AMD-7600-8G': 'productos/rx7900xtx.jpg',
    'CPU-INTEL-14900K': 'productos/intel14th.jpg',
    'CPU-INTEL-14700K': 'productos/intel14th.jpg',
    'CPU-INTEL-14600K': 'productos/intel14th.jpg',
    'CPU-INTEL-14400F': 'productos/intel14th.jpg',
    'CPU-INTEL-14100': 'productos/intel14th.jpg',
    'MB-GB-B760M-AORUS': 'productos/motherboard_z790.jpg',
    'MB-ASUS-Z790-MAX': 'productos/motherboard_z790.jpg',
    'RAM-KIN-DDR4-16G3200': 'productos/ram_ddr4.jpg',
    'RAM-KIN-DDR4-8G2666': 'productos/ram_ddr4.jpg',
    'HDD-WD-BLUE-2TB': 'productos/hdd_wd.jpg',
    'COOL-DC-AK620D': 'productos/cooler_ak620.jpg',
    'FAN-COR-SP120-3PK': 'productos/fans_rgb.jpg',
}

HARDWARE_SPECS = {
    # GPU
    'GPU-ASUS-RTX4090-24G': {
        'VRAM / Memoria': '24 GB GDDR6X',
        'Bus de Memoria': '384-bit',
        'Núcleos CUDA': '16,384',
        'Frecuencia Boost': '2,640 MHz (Modo OC)',
        'Interfaz': 'PCIe 4.0 x16',
        'TDP / Consumo': '450 Watts',
        'Conectores de Poder': '1x 16-pin (12VHPWR)',
        'Salidas de Video': '2x HDMI 2.1a, 3x DisplayPort 1.4a',
        'Dimensiones': '357.6 x 149.3 x 70.1 mm (3.5 slots)',
        'Fuente Recomendada': '1000 Watts'
    },
    'GPU-MSI-RTX4080S-16G': {
        'VRAM / Memoria': '16 GB GDDR6X',
        'Bus de Memoria': '256-bit',
        'Núcleos CUDA': '10,240',
        'Frecuencia Boost': '2,610 MHz',
        'Interfaz': 'PCIe 4.0 x16',
        'TDP / Consumo': '320 Watts',
        'Conectores de Poder': '1x 16-pin (12VHPWR)',
        'Salidas de Video': '1x HDMI 2.1a, 3x DisplayPort 1.4a',
        'Dimensiones': '322 x 136 x 62 mm',
        'Fuente Recomendada': '750 Watts'
    },
    'GPU-ASUS-RTX4070S-12G': {
        'VRAM / Memoria': '12 GB GDDR6X',
        'Bus de Memoria': '192-bit',
        'Núcleos CUDA': '7,168',
        'Frecuencia Boost': '2,595 MHz',
        'Interfaz': 'PCIe 4.0 x16',
        'TDP / Consumo': '220 Watts',
        'Salidas de Video': '1x HDMI 2.1a, 3x DisplayPort 1.4a',
        'Fuente Recomendada': '650 Watts'
    },
    'GPU-GB-RTX4070-12G': {
        'VRAM / Memoria': '12 GB GDDR6X',
        'Bus de Memoria': '192-bit',
        'Núcleos CUDA': '5,888',
        'Frecuencia Boost': '2,490 MHz',
        'Interfaz': 'PCIe 4.0 x16',
        'TDP / Consumo': '200 Watts',
        'Refrigeración': 'Triple ventilador Windforce',
        'Fuente Recomendada': '650 Watts'
    },
    'GPU-MSI-RTX4060TI-16G': {
        'VRAM / Memoria': '16 GB GDDR6',
        'Bus de Memoria': '128-bit',
        'Núcleos CUDA': '4,352',
        'Frecuencia Boost': '2,565 MHz',
        'Interfaz': 'PCIe 4.0 x8 (x16 slot)',
        'TDP / Consumo': '165 Watts',
        'Fuente Recomendada': '550 Watts'
    },
    'GPU-ASUS-RTX4060-8G': {
        'VRAM / Memoria': '8 GB GDDR6',
        'Bus de Memoria': '128-bit',
        'Núcleos CUDA': '3,072',
        'Frecuencia Boost': '2,535 MHz',
        'TDP / Consumo': '115 Watts',
        'Fuente Recomendada': '500 Watts'
    },
    'GPU-MSI-RTX4060-8G': {
        'VRAM / Memoria': '8 GB GDDR6',
        'Bus de Memoria': '128-bit',
        'Núcleos CUDA': '3,072',
        'Frecuencia Boost': '2,490 MHz',
        'TDP / Consumo': '115 Watts',
        'Refrigeración': 'Dual Fan Ventus 2X',
        'Fuente Recomendada': '500 Watts'
    },
    'GPU-ASUS-RTX5070-16G': {
        'VRAM / Memoria': '16 GB GDDR7',
        'Bus de Memoria': '256-bit',
        'Arquitectura': 'NVIDIA Blackwell',
        'Frecuencia Boost': '2,750 MHz',
        'TDP / Consumo': '250 Watts',
        'Conector de Poder': '1x 16-pin (12V-2x6)',
        'Fuente Recomendada': '750 Watts'
    },
    'GPU-AMD-7900XTX-24G': {
        'VRAM / Memoria': '24 GB GDDR6',
        'Bus de Memoria': '384-bit',
        'Stream Processors': '6,144',
        'Infinity Cache': '96 MB',
        'Frecuencia Boost': '2,680 MHz',
        'TDP / Consumo': '355 Watts',
        'Salidas de Video': '2x HDMI 2.1, 2x DisplayPort 2.1',
        'Fuente Recomendada': '850 Watts'
    },
    'GPU-AMD-7800XT-16G': {
        'VRAM / Memoria': '16 GB GDDR6',
        'Bus de Memoria': '256-bit',
        'Stream Processors': '3,840',
        'Infinity Cache': '64 MB',
        'Frecuencia Boost': '2,565 MHz',
        'TDP / Consumo': '263 Watts',
        'Fuente Recomendada': '700 Watts'
    },
    'GPU-AMD-7700XT-12G': {
        'VRAM / Memoria': '12 GB GDDR6',
        'Bus de Memoria': '192-bit',
        'Stream Processors': '3,456',
        'Infinity Cache': '48 MB',
        'Frecuencia Boost': '2,599 MHz',
        'TDP / Consumo': '245 Watts',
        'Fuente Recomendada': '700 Watts'
    },
    'GPU-AMD-7600-8G': {
        'VRAM / Memoria': '8 GB GDDR6',
        'Bus de Memoria': '128-bit',
        'Stream Processors': '2,048',
        'Infinity Cache': '32 MB',
        'Frecuencia Boost': '2,655 MHz',
        'TDP / Consumo': '165 Watts',
        'Fuente Recomendada': '550 Watts'
    },

    # CPU AMD
    'CPU-AMD-7800X3D': {
        'Socket': 'Socket AM5',
        'Núcleos / Hilos': '8 Núcleos / 16 Hilos',
        'Frecuencia Base': '4.2 GHz',
        'Frecuencia Max Boost': '5.0 GHz',
        'Memoria Caché L3': '96 MB (AMD 3D V-Cache)',
        'TDP / Consumo': '120 Watts',
        'Litografía': 'TSMC 5nm FinFET',
        'Gráficos Integrados': 'AMD Radeon Graphics (RDNA 2)',
        'Memoria Soportada': 'DDR5 hasta 5200 MT/s (Dual Channel)',
        'Desbloqueado para OC': 'Sí (PBO / Curve Optimizer)'
    },
    'CPU-AMD-7600X': {
        'Socket': 'Socket AM5',
        'Núcleos / Hilos': '6 Núcleos / 12 Hilos',
        'Frecuencia Base': '4.7 GHz',
        'Frecuencia Max Boost': '5.3 GHz',
        'Memoria Caché L3': '32 MB',
        'TDP / Consumo': '105 Watts',
        'Litografía': 'TSMC 5nm FinFET',
        'Gráficos Integrados': 'AMD Radeon Graphics'
    },
    'CPU-AMD-7600': {
        'Socket': 'Socket AM5',
        'Núcleos / Hilos': '6 Núcleos / 12 Hilos',
        'Frecuencia Base': '3.8 GHz',
        'Frecuencia Max Boost': '5.1 GHz',
        'Memoria Caché L3': '32 MB',
        'TDP / Consumo': '65 Watts',
        'Cooler Incluido': 'AMD Wraith Stealth'
    },
    'CPU-AMD-7900': {
        'Socket': 'Socket AM5',
        'Núcleos / Hilos': '12 Núcleos / 24 Hilos',
        'Frecuencia Base': '3.7 GHz',
        'Frecuencia Max Boost': '5.4 GHz',
        'Memoria Caché L3': '64 MB',
        'TDP / Consumo': '65 Watts'
    },
    'CPU-AMD-7950X': {
        'Socket': 'Socket AM5',
        'Núcleos / Hilos': '16 Núcleos / 32 Hilos',
        'Frecuencia Base': '4.5 GHz',
        'Frecuencia Max Boost': '5.7 GHz',
        'Memoria Caché L3': '64 MB',
        'TDP / Consumo': '170 Watts'
    },
    'CPU-AMD-5600': {
        'Socket': 'Socket AM4',
        'Núcleos / Hilos': '6 Núcleos / 12 Hilos',
        'Frecuencia Base': '3.5 GHz',
        'Frecuencia Max Boost': '4.4 GHz',
        'Memoria Caché L3': '32 MB',
        'TDP / Consumo': '65 Watts',
        'Memoria Soportada': 'DDR4 hasta 3200 MT/s'
    },

    # CPU INTEL
    'CPU-INTEL-14900K': {
        'Socket': 'LGA1700',
        'Núcleos / Hilos': '24 Núcleos (8P + 16E) / 32 Hilos',
        'Frecuencia Base P-Core': '3.2 GHz',
        'Frecuencia Turbo Max': '6.0 GHz (Thermal Velocity Boost)',
        'Caché Intel Smart': '36 MB',
        'TDP Base': '125 Watts (Max Turbo 253W)',
        'Gráficos Integrados': 'Intel UHD Graphics 770',
        'Memoria Soportada': 'DDR5 5600 MT/s / DDR4 3200 MT/s'
    },
    'CPU-INTEL-14700K': {
        'Socket': 'LGA1700',
        'Núcleos / Hilos': '20 Núcleos (8P + 12E) / 28 Hilos',
        'Frecuencia Base P-Core': '3.4 GHz',
        'Frecuencia Turbo Max': '5.6 GHz',
        'Caché Intel Smart': '33 MB',
        'TDP Base': '125 Watts (Max Turbo 253W)',
        'Gráficos Integrados': 'Intel UHD Graphics 770'
    },
    'CPU-INTEL-14600K': {
        'Socket': 'LGA1700',
        'Núcleos / Hilos': '14 Núcleos (6P + 8E) / 20 Hilos',
        'Frecuencia Base P-Core': '3.5 GHz',
        'Frecuencia Turbo Max': '5.3 GHz',
        'Caché Intel Smart': '24 MB',
        'TDP Base': '125 Watts (Max Turbo 181W)'
    },
    'CPU-INTEL-14400F': {
        'Socket': 'LGA1700',
        'Núcleos / Hilos': '10 Núcleos (6P + 4E) / 16 Hilos',
        'Frecuencia Base P-Core': '2.5 GHz',
        'Frecuencia Turbo Max': '4.7 GHz',
        'Caché Intel Smart': '20 MB',
        'TDP Base': '65 Watts (Max Turbo 148W)',
        'Gráficos Integrados': 'No (Requiere GPU dedicada)'
    },
    'CPU-INTEL-14100': {
        'Socket': 'LGA1700',
        'Núcleos / Hilos': '4 Núcleos (4P + 0E) / 8 Hilos',
        'Frecuencia Base P-Core': '3.5 GHz',
        'Frecuencia Turbo Max': '4.7 GHz',
        'Caché Intel Smart': '12 MB',
        'TDP Base': '60 Watts (Max Turbo 110W)',
        'Gráficos Integrados': 'Intel UHD Graphics 730'
    },

    # PLACAS MADRE
    'MB-ASUS-TUF-B650P': {
        'Socket': 'Socket AM5',
        'Chipset': 'AMD B650',
        'Factor de Forma': 'ATX (30.5 x 24.4 cm)',
        'Fases de Poder': '12+2 DrMOS (60A)',
        'Ranuras RAM': '4x DDR5 hasta 7600+ MHz (OC) / 192GB Máx',
        'Ranuras PCIe': '1x PCIe 5.0 x16, 1x PCIe 4.0 x16, 2x PCIe 4.0 x1',
        'Almacenamiento': '1x M.2 PCIe 5.0 x4, 2x M.2 PCIe 4.0 x4, 4x SATA 6Gb/s',
        'Red y Conectividad': 'Realtek 2.5Gb Ethernet + Wi-Fi 6 + Bluetooth 5.2',
        'Audio': 'Realtek 7.1 Surround Sound de Alta Definición'
    },
    'MB-MSI-B650-TOMA': {
        'Socket': 'Socket AM5',
        'Chipset': 'AMD B650',
        'Factor de Forma': 'ATX',
        'Fases de Poder': '14+2+1 Duet Rail Power System',
        'Ranuras RAM': '4x DDR5 hasta 6600+ MHz',
        'Almacenamiento': '3x M.2 PCIe 4.0 x4, 6x SATA 6Gb/s',
        'Red': '2.5G LAN + AMD Wi-Fi 6E'
    },
    'MB-GB-B760M-AORUS': {
        'Socket': 'LGA1700 (Intel 12va, 13ra y 14ta Gen)',
        'Chipset': 'Intel B760',
        'Factor de Forma': 'Micro-ATX',
        'Ranuras RAM': '4x DDR5 hasta 7600 MHz (OC)',
        'Red': 'Realtek 2.5GbE LAN + Wi-Fi 6E'
    },
    'MB-ASUS-Z790-MAX': {
        'Socket': 'LGA1700',
        'Chipset': 'Intel Z790',
        'Factor de Forma': 'ATX',
        'Fases de Poder': '20+1+2 Fases (90A)',
        'Ranuras PCIe': '2x PCIe 5.0 x16 SafeSlots',
        'Almacenamiento': '5x M.2 Slots (1x PCIe 5.0 M.2 con disipador masivo)',
        'Thunderbolt': '2x Puertos Thunderbolt 4 Type-C (40 Gbps)',
        'Red y WiFi': 'Intel 2.5Gb Ethernet + Intel Wi-Fi 7'
    },

    # RAM
    'RAM-COR-DDR5-32G6000': {
        'Tipo de Memoria': 'DDR5 Desktop DIMM (288-pin)',
        'Capacidad': '32 GB (2 x 16 GB)',
        'Frecuencia': '6000 MHz (PC5-48000)',
        'Latencia CAS': 'CL30 (30-36-36-76)',
        'Voltaje': '1.35 V',
        'Perfiles de Rendimiento': 'AMD EXPO & Intel XMP 3.0',
        'Iluminación': 'RGB dinámico de diez zonas Corsair iCUE',
        'Disipador': 'Aluminio anodizado negro mate'
    },
    'RAM-COR-DDR5-64G6400': {
        'Tipo de Memoria': 'DDR5 Desktop DIMM',
        'Capacidad': '64 GB (2 x 32 GB)',
        'Frecuencia': '6400 MHz',
        'Latencia CAS': 'CL32',
        'Voltaje': '1.40 V',
        'Iluminación': '11 LEDs RGB direccionables individualmente',
        'Disipador': 'Dominator Titanium de aluminio forjado'
    },
    'RAM-KIN-DDR4-16G3200': {
        'Tipo de Memoria': 'DDR4 Desktop DIMM',
        'Capacidad': '16 GB (2 x 8 GB)',
        'Frecuencia': '3200 MHz (PC4-25600)',
        'Latencia CAS': 'CL16',
        'Voltaje': '1.35 V',
        'Perfil': 'Intel XMP Ready'
    },
    'RAM-KIN-DDR4-8G2666': {
        'Tipo de Memoria': 'DDR4 Desktop DIMM',
        'Capacidad': '8 GB (1 x 8 GB)',
        'Frecuencia': '2666 MHz',
        'Latencia CAS': 'CL19',
        'Voltaje': '1.20 V'
    },

    # ALMACENAMIENTO
    'SSD-KIN-KC3000-2TB': {
        'Factor de Forma': 'M.2 2280',
        'Interfaz': 'PCIe 4.0 x4 NVMe 1.4',
        'Capacidad': '2048 GB (2 TB)',
        'Controlador': 'Phison PS5018-E18',
        'Lectura Secuencial': 'Hasta 7,000 MB/s',
        'Escritura Secuencial': 'Hasta 7,000 MB/s',
        'Lectura Aleatoria 4K': 'Hasta 1,000,000 IOPS',
        'Resistencia (TBW)': '1,600 TBW',
        'Disipador Térmico': 'Lámina de grafeno y aluminio de bajo perfil'
    },
    'SSD-WD-SN850X-1TB': {
        'Factor de Forma': 'M.2 2280',
        'Interfaz': 'PCIe 4.0 x4 NVMe',
        'Capacidad': '1 TB (1000 GB)',
        'Lectura Secuencial': 'Hasta 7,300 MB/s',
        'Escritura Secuencial': 'Hasta 6,300 MB/s',
        'Resistencia (TBW)': '600 TBW'
    },
    'HDD-WD-BLUE-2TB': {
        'Factor de Forma': '3.5 pulgadas',
        'Capacidad': '2 TB (2000 GB)',
        'Interfaz': 'SATA 6 Gb/s (SATA III)',
        'Velocidad de Rotación': '7200 RPM',
        'Memoria Caché': '256 MB',
        'Tasa de Transferencia': 'Hasta 215 MB/s',
        'Tecnología de Grabación': 'CMR (Conventional Magnetic Recording)'
    },

    # FUENTES DE PODER
    'PSU-COR-RM1000X': {
        'Potencia Nominal': '1000 Watts',
        'Eficiencia Energética': 'Certificación 80 PLUS Gold (hasta 90%)',
        'Modularidad': '100% Full Modular',
        'Ventilador': '135mm con levitación magnética (Modo Zero RPM)',
        'Conectores': '1x ATX 24-pin, 3x EPS 8-pin, 6x PCIe 8-pin, 14x SATA',
        'Condensadores': '100% japoneses certificados a 105°C',
        'Garantía': '10 años oficial del fabricante'
    },
    'PSU-SEA-GX850': {
        'Potencia Nominal': '850 Watts',
        'Eficiencia': '80 PLUS Gold',
        'Modularidad': 'Full Modular',
        'Estándar': 'ATX 3.0 / PCIe 5.0 (Cable 12VHPWR 16-pin incluido)',
        'Ventilador': '135mm FDB con control híbrido silencioso'
    },
    'PSU-MSI-A650BN': {
        'Potencia Nominal': '650 Watts',
        'Eficiencia': '80 PLUS Bronze (hasta 85%)',
        'Cables': 'Cables planos color negro',
        'Ventilador': '120mm silencioso de bajo ruido',
        'Protecciones': 'OVP, OCP, SCP, OPP, OTP'
    },

    # GABINETES
    'CASE-NZXT-H5F-BK': {
        'Tipo de Gabinete': 'Mid-Tower ATX',
        'Dimensiones': '464 x 227 x 446 mm',
        'Material': 'Acero SGCC y Vidrio Templado oscurecido',
        'Soporte Motherboard': 'ATX, Micro-ATX, Mini-ITX',
        'Ventiladores Incluidos': '2x F140 RGB Core frontales + 2x F120Q (trasero e inferior)',
        'Soporte Radiador': 'Hasta 280mm frontal / 240mm superior',
        'Longitud Máxima GPU': 'Hasta 365 mm; descontar espacio de ventiladores o radiador frontal',
        'Conectividad Frontal': '1x USB-C, 1x USB-A, jack combinado de 3.5 mm'
    },
    'CASE-COR-4000D-AIR': {
        'Tipo de Gabinete': 'Mid-Tower ATX',
        'Panel Frontal': 'Malla triangular de alto flujo de aire',
        'Soporte Motherboard': 'ATX, Micro-ATX, Mini-ITX',
        'Ventiladores Incluidos': '2x Corsair AirGuide 120mm',
        'Dimensiones (largo × ancho × alto)': '453 × 230 × 466 mm',
        'Capacidad de Ventilación': 'Hasta 6 ventiladores de 120 mm o 4 de 140 mm'
    },

    # REFRIGERACION
    'COOL-NZXT-KR360': {
        'Tipo': 'Refrigeración Líquida Todo en Uno (AIO)',
        'Tamaño Radiador': 'Clase 360 mm; radiador de aluminio',
        'Ventiladores': '3x 120 mm F120 RGB Core + controlador RGB NZXT',
        'Display de Bomba': 'Panel LCD de 1.54 pulgadas, 240 × 240 px',
        'Compatibilidad Socket': 'Intel LGA 1700/1200/115X, AMD AM5/AM4',
        'Bomba': 'Motor Asetek de 7ma generación (800 - 2,800 RPM)'
    },
    'COOL-DC-AK620D': {
        'Tipo': 'Cooler por aire de doble torre',
        'Tubos de Calor': '6x Heatpipes de cobre niquelado de 6 mm',
        'Ventiladores': '2x 120mm PWM Fluid Dynamic Bearing (FDB)',
        'Pantalla Digital': 'Display en tiempo real de temperatura y uso de CPU',
        'Velocidad de Ventiladores': '500–1850 RPM (±10%), PWM de 4 pines',
        'Altura Total': '162 mm',
        'Compatibilidad': 'Intel LGA1700/1200/115X, AMD AM5/AM4'
    },
    'FAN-COR-SP120-3PK': {
        'Contenido': 'Pack de 3 Ventiladores + Controlador Lighting Node CORE',
        'Dimensiones': '120 x 120 x 25 mm',
        'Velocidad de Giro': '400–1500 RPM (control PWM)',
        'Flujo de Aire': '47.73 CFM',
        'Presión Estática': '1.46 mm-H2O',
        'Iluminación': '8 LEDs RGB direccionables individualmente por ventilador'
    }
}
