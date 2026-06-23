-- ============================================================
-- Script para dejar el sistema en 0 (excepto el usuario id=1)
-- 365 Viajes - Reset completo de datos
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------
-- reservas app
-- -------------------------
TRUNCATE TABLE reservas_ordenserviciodetalle;
TRUNCATE TABLE reservas_ordenservicio;
TRUNCATE TABLE reservas_reservaadicionaldetalle;
TRUNCATE TABLE reservas_reservadetalle;
TRUNCATE TABLE reservas_reserva;
TRUNCATE TABLE reservas_gasto;

-- -------------------------
-- base app
-- -------------------------
TRUNCATE TABLE base_auditoria;
TRUNCATE TABLE base_ordenserviciocolumna;
TRUNCATE TABLE base_servicioparada;
TRUNCATE TABLE base_servicioprecioespecial;
TRUNCATE TABLE base_adicionalprecioespecial;
TRUNCATE TABLE base_horario;
TRUNCATE TABLE base_servicio;
TRUNCATE TABLE base_adicional;
TRUNCATE TABLE base_lugar;
TRUNCATE TABLE base_cliente;
TRUNCATE TABLE base_guia;
TRUNCATE TABLE base_chofer;
TRUNCATE TABLE base_responsable;
TRUNCATE TABLE base_opciongeneral;

-- -------------------------
-- Django internals
-- -------------------------
TRUNCATE TABLE django_admin_log;
TRUNCATE TABLE django_session;

-- Eliminar todos los usuarios EXCEPTO el id=1
DELETE FROM auth_user_groups WHERE user_id != 1;
DELETE FROM auth_user_user_permissions WHERE user_id != 1;
DELETE FROM auth_user WHERE id != 1;

SET FOREIGN_KEY_CHECKS = 1;
