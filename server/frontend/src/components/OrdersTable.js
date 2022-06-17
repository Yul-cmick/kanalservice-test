import React from 'react';

function OrdersTable(props) {
    const { orders } = props;
    if (!orders || orders.length === 0) return <p>Нет данных.</p>

    return (
        <table className="table">
            <thead>
                <tr>
                    <th>№</th>
                    <th>Заказ №</th>
                    <th>Стоимость, $</th>
                    <th>Срок поставки</th>
                    <th>Стоимость, ₽</th>
                </tr>
            </thead>
            <tbody>
            {
                orders.map((order) => 
                    <tr key={order.order_id}>
                        <td>{order.id}</td>
                        <td>{order.order_id}</td>
                        <td>{order.usd_cost}</td>
                        <td>{order.delivery_date} </td>
                        <td>{order.rub_cost}</td>
                    </tr>
                )
            }
            </tbody>
        </table>
    )
}

export default OrdersTable;