import React, { useContext } from 'react'
import { Context } from '../Context/AppContextProvider'
import TimeFrames from './TimeFrames'

export default function StockBar() {

  const {stockToken, stockList} = useContext(Context)


  return (
    <nav className="navbar navbar-expand-lg navbar-white bg-white">
      <div className="container-fluid">
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item px-3">
              <p className='p-1'>{stockList[stockToken]}</p>
            </li>
            <TimeFrames/>
          </ul>
          <form className="d-flex">
            <input className="form-control me-2" type="search" placeholder="Search" aria-label="Search"/>
            <button className="btn btn-outline-success" type="submit">Search</button>
          </form>
        </div>
      </div>
    </nav>
  )
}
