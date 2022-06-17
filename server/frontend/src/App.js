import './App.css';
import axios from 'axios'
import React from 'react';
import OrdersTable from './components/OrdersTable'
import TotalSum from './components/TotalSum'

export default class App extends React.Component {
  state = {
    total_sum: 0,
    orders: [],
  }

  componentDidMount() {
    axios.get('api/all_orders').then((resp) => {
      const orders = resp.data.orders;
      this.setState({
        ...this.state,
        orders: orders
      });
    });
    axios.get('api/total_sum').then((resp) => {
      const total_sum = resp.data.total_sum;
      this.setState({
        ...this.state,
        total_sum: total_sum
      });
    });
  }

  render() {
    return (
      <div className="App">
        <TotalSum total_sum={this.state.total_sum}/>
        <OrdersTable orders={this.state.orders}/>
      </div>
    );
  }
}
