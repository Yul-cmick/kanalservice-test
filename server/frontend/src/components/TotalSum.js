import React from 'react';

function TotalSum(props) {
    const { total_sum } = props;
    if (!total_sum) {
        return <p>Нет данных.</p>
    }

    return (
        <div>
            <span className="total_sum">Итого: {total_sum} ₽ </span>
        </div>
    )
}

export default TotalSum;