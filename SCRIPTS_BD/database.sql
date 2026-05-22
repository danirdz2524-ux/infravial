-- ============================================================
-- 1. TABLA DE USUARIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user', -- 'admin' o 'user'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insertar usuario administrador por defecto
INSERT INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin')
ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- 2. TABLA DE ALCANTARILLAS (FICHAS TÉCNICAS)
-- ============================================================
CREATE TABLE IF NOT EXISTS alcantarillas (
    id BIGSERIAL PRIMARY KEY,
    ficha_numero BIGSERIAL UNIQUE,   -- Número automático y único
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Ubicación y datos generales
    fecha DATE,
    provincia TEXT,
    canton TEXT,
    parroquia TEXT,
    tramo_vial TEXT,
    
    -- MUROS DE ALA
    muro_ala_longitud TEXT,
    muro_ala_espesor TEXT,
    muro_ala_solera BOOLEAN,
    muro_ala_material TEXT,
    muro_ala_estado TEXT,
    
    -- TUBERÍA
    tuberia_material TEXT,
    tuberia_longitud TEXT,
    tuberia_diametro TEXT,
    tuberia_estado TEXT,
    
    -- MURO CABEZAL
    muro_cabezal_longitud TEXT,
    muro_cabezal_espesor TEXT,
    muro_cabezal_estado TEXT,
    
    -- POZO DE RECOLECCIÓN
    pozo_recoleccion BOOLEAN,
    pozo_ancho TEXT,
    pozo_largo TEXT,
    pozo_estado TEXT,
    
    -- Coordenadas UTM
    utm_este TEXT,
    utm_norte TEXT,
    
    -- Observaciones y fotografía
    observaciones TEXT,
    imagen TEXT,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 3. TABLA DE AUDITORÍA (BITÁCORA DE ACTIVIDAD)
-- ============================================================
CREATE TABLE IF NOT EXISTS auditoria (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    username TEXT,
    accion TEXT,
    detalles TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 4. ÍNDICES PARA MEJORAR EL RENDIMIENTO
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_alcantarillas_ficha_numero ON alcantarillas(ficha_numero);
CREATE INDEX IF NOT EXISTS idx_alcantarillas_provincia ON alcantarillas(provincia);
CREATE INDEX IF NOT EXISTS idx_alcantarillas_canton ON alcantarillas(canton);
CREATE INDEX IF NOT EXISTS idx_auditoria_created_at ON auditoria(created_at);

-- ============================================================
-- 5. CONSULTAS DE VERIFICACIÓN (OPCIONALES)
-- ============================================================
-- Ver todos los usuarios
-- SELECT * FROM users;

-- Ver todas las fichas
-- SELECT * FROM alcantarillas;

-- Ver la actividad reciente
-- SELECT * FROM auditoria ORDER BY created_at DESC LIMIT 10;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================