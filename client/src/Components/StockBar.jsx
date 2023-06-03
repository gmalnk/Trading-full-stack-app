import React, { useContext } from 'react'
import { Context } from '../Context/AppContextProvider'
import TimeFrames from './TimeFrames'

export default function StockBar() {

  const {stockToken, stockList, setSearchActive} = useContext(Context)

  const handleOnClickName = () => {
    setSearchActive(true)
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-white bg-white">
      <div className="container-fluid">
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item px-3">
              <p className='p-1' onClick={()=> handleOnClickName()}>{stockList[stockToken]}</p>
            </li>
            <TimeFrames/>
          </ul>
        </div>
      </div>
    </nav>
  )
}
