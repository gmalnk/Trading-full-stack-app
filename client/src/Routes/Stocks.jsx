import React from 'react'
import StockBar from '../Components/StockBar'
import ChartComponent from '../Components/Chart'
import StockList from '../Components/StockList'

export default function Stocks() {
  return (
    <div className='container-fluid'>
        <div className='row'>
            <StockBar />
        </div>
        <div className='row'>
            <div className='col-10'>
              <ChartComponent/>
            </div>
            <div className='col-2'>
              <StockList/>
            </div>
        </div>
    </div>
  )
}
