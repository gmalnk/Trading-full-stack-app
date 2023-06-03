import React, { useContext } from 'react'
import StockBar from '../Components/StockBar'
import ChartComponent from '../Components/Chart'
import StockList from '../Components/StockList'
import Search from '../Components/Search'
import Screen from '../Components/Screen'
import { Context } from '../Context/AppContextProvider'

export default function Stocks() {
  const {searchActive} = useContext(Context)

  return (
    <div className='.container-fluid'>
      {searchActive && <Screen/>}
      <div className='container-fluid blur'>
          {searchActive && <Search/>}
          <div style = {searchActive? {filter: "blur(2px)"} : {}}>
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
      </div>
    </div>
  )
}
