select * from venta where DATE(fecha) = '2026-02-20';
select * from detalle_venta;
select * from venta;

-- Ventas diarias
SELECT
    t.fecha,
    t.QR,
    t.Efectivo,
    t.TotalVentas,
    t.CostoProd,
    COALESCE((
        SELECT SUM(c.monto)
        FROM caja c
        WHERE c.tipo = 'EGRESO'
          AND DATE(c.fecha) = t.fecha
    ), 0) AS Gastos,
    t.TotalVentas - t.CostoProd - COALESCE((
        SELECT SUM(c.monto)
        FROM caja c
        WHERE c.tipo = 'EGRESO'
          AND DATE(c.fecha) = t.fecha
    ), 0) AS Ganancia
FROM (
    SELECT
        DATE(v.fecha) AS fecha,
        SUM(
            CASE 
                WHEN v.metodo_pago = 'QR' 
                THEN dv.precio_unitario * dv.cantidad
                ELSE 0
            END
        ) AS QR,
        SUM(
            CASE 
                WHEN v.metodo_pago = 'Efectivo' 
                THEN dv.precio_unitario * dv.cantidad
                ELSE 0
            END
        ) AS Efectivo,
        SUM(dv.precio_unitario * dv.cantidad) AS TotalVentas,
        SUM(dv.costo_unitario * dv.cantidad) AS CostoProd
    FROM venta v
    JOIN detalle_venta dv ON v.id = dv.venta_id
    GROUP BY DATE(v.fecha)
) t
ORDER BY t.fecha DESC;

-- Ventas Mensuales
SELECT
    EXTRACT(YEAR FROM v.fecha) AS anio,
    EXTRACT(MONTH FROM v.fecha) AS mes,
    SUM(
        CASE 
            WHEN v.metodo_pago = 'QR' 
            THEN dv.precio_unitario * dv.cantidad
            ELSE 0
        END
    ) AS QR,
    SUM(
        CASE 
            WHEN v.metodo_pago = 'Efectivo' 
            THEN dv.precio_unitario * dv.cantidad
            ELSE 0
        END
    ) AS Efectivo,
    SUM(dv.precio_unitario * dv.cantidad) AS TotalVentas,
    SUM(dv.costo_unitario * dv.cantidad) AS CostoProd,
    SUM(dv.precio_unitario * dv.cantidad) - SUM(dv.costo_unitario * dv.cantidad) AS Utilidad
FROM venta v
JOIN detalle_venta dv ON v.id = dv.venta_id
GROUP BY
    EXTRACT(YEAR FROM v.fecha),
    EXTRACT(MONTH FROM v.fecha)
ORDER BY
    anio DESC,
    mes DESC;
----------------------------------
SELECT
    t.anio,
    t.mes,
    t.QR,
    t.Efectivo,
    t.TotalVentas,
    t.CostoProd,
    COALESCE(g.total_gasto, 0) + COALESCE(c.total_caja, 0) AS Total_Gastos,
    t.TotalVentas - t.CostoProd 
    - (COALESCE(g.total_gasto, 0) + COALESCE(c.total_caja, 0)) AS Utilidad
FROM (
    SELECT
        EXTRACT(YEAR FROM v.fecha) AS anio,
        EXTRACT(MONTH FROM v.fecha) AS mes,
        SUM(
            CASE 
                WHEN v.metodo_pago = 'QR' 
                THEN dv.precio_unitario * dv.cantidad
                ELSE 0
            END
        ) AS QR,
        SUM(
            CASE 
                WHEN v.metodo_pago = 'Efectivo' 
                THEN dv.precio_unitario * dv.cantidad
                ELSE 0
            END
        ) AS Efectivo,
        SUM(dv.precio_unitario * dv.cantidad) AS TotalVentas,
        SUM(dv.costo_unitario * dv.cantidad) AS CostoProd
    FROM venta v
    JOIN detalle_venta dv ON v.id = dv.venta_id
    GROUP BY
        EXTRACT(YEAR FROM v.fecha),
        EXTRACT(MONTH FROM v.fecha)
) t
LEFT JOIN (
    SELECT
        EXTRACT(YEAR FROM fecha) AS anio,
        EXTRACT(MONTH FROM fecha) AS mes,
        SUM(monto) AS total_gasto
    FROM gasto
    GROUP BY
        EXTRACT(YEAR FROM fecha),
        EXTRACT(MONTH FROM fecha)
) g
ON g.anio = t.anio AND g.mes = t.mes
LEFT JOIN (
    SELECT
        EXTRACT(YEAR FROM fecha) AS anio,
        EXTRACT(MONTH FROM fecha) AS mes,
        SUM(monto) AS total_caja
    FROM caja
    WHERE tipo = 'EGRESO'
    GROUP BY
        EXTRACT(YEAR FROM fecha),
        EXTRACT(MONTH FROM fecha)
) c
ON c.anio = t.anio AND c.mes = t.mes
ORDER BY
    t.anio DESC,
    t.mes DESC;
----------------------------------
select * from caja where tipo='EGRESO';

select
	sum(monto) +
	(
		SELECT SUM(c.monto)
        FROM caja c
        WHERE c.tipo = 'EGRESO'
	) as Total_gasto
from gasto;