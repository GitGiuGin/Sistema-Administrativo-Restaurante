select
	*
from caja c join turno_caja tc
on tc.id = c.turno_id;

select
	c.fecha,
	u.username as Usuario,
	sum(case
		when v.metodo_pago = 'QR' then v.total
 	END) as Total_QR,
	sum(case
		when v.metodo_pago = 'Efectivo' then v.total
 	END) as Total_efectivo,
	tc.monto_cierre as Declarado,
	tc.abierta
from caja c join turno_caja tc
on tc.id = c.turno_id join venta v
on v.id = c.venta_id join usuario u
on tc.usuario_id = u.id
group by tc.id, u.username, tc.abierta, tc.monto_cierre, c.fecha
order by c.fecha desc;

SELECT
    tc.fecha_apertura AS fecha,
    u.username AS usuario,
    SUM(
        CASE 
            WHEN v.metodo_pago = 'QR' THEN v.total
            ELSE 0
        END
    ) AS total_qr,
    SUM(
        CASE 
            WHEN v.metodo_pago = 'Efectivo' THEN v.total
            ELSE 0
        END
	) - SUM(
    	CASE 
        	WHEN c.tipo = 'EGRESO' THEN c.monto
			ELSE 0
    	END
	) AS total_efectivo,
    tc.monto_cierre AS declarado,
	tc.monto_cierre - SUM(v.total) AS diferencia,
    tc.abierta
FROM turno_caja tc
JOIN caja c ON c.turno_id = tc.id
LEFT JOIN venta v ON v.id = c.venta_id
JOIN usuario u ON tc.usuario_id = u.id
where tc.id=5
GROUP BY 
    tc.id,
    u.username,
    tc.monto_cierre,
    tc.abierta
ORDER BY tc.fecha_apertura DESC;
