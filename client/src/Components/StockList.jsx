import React, { useContext, useState, useEffect } from 'react'
import AxiosAPI from '../API/AxiosAPI'
import AppContextProvider, { Context } from '../Context/AppContextProvider'



export default function StockList() {
  const {setStockToken, stockList, setStockList} = useContext(Context)
  const [divHeight, setDivHeight] = useState(window.innerHeight - 100);

  useEffect(() => {
    const handleResize = () => {
      setDivHeight(window.innerHeight - 100);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const divStyle = {
    height: `${divHeight}px`,
    overflow:"auto",
  };


  const fetchAllStocksData = async () =>{
    const response = await AxiosAPI.get("/stocklist")
    console.log(response)
    setStockList(response.data)
  }

  const handleClickOnStock = (key) => {
    setStockToken(key)
  }


  useEffect(()=>{
    fetchAllStocksData()
  },[])


  return (
    <div className='col' style={divStyle} >
      {Object.keys(stockList).map( (key)=>{
        return (<div id= {key} onClick={()=>handleClickOnStock(key)} className='row px-3'>
                {stockList[key]}
                </div>)
      })}
    </div>
  )
}
