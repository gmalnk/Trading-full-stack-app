import React, { useContext, useEffect, useState } from 'react'
import { Context } from '../Context/AppContextProvider'

export default function Search() {
    const {stockList, setStockToken, setSearchActive} = useContext(Context);
    const stocks = Object.values(stockList).sort();
    const keys = Object.keys(stockList);
    const [searchList, setSearchList] = useState([])
    const [search, setSearch] = useState("")

    const handleOnChangeInput = (value)=>{
        setSearch(value.toUpperCase())
        console.log(value)
        value !== ""? filterSearchList(value)  : getInitialList()
    }

    const handleOnClickSearchItem = (value) =>{
        for (let i=0 ; i <= stocks.length; i++){
            if (stockList[keys[i]] === value){
                console.log(keys[i])
                setStockToken(keys[i])
                setSearchActive(false)
                break;
            }
        }
    }

    const filterSearchList = (value)=>{
        let filteredList = [];
        let count = 0;
        for (let i=0; i < stocks.length ; i++){
            if (stocks[i].toLowerCase().includes(value.toLowerCase()))  {
                filteredList.push(stocks[i]);
                count++;
            }
            if( count >= 10){
                break;
            }
        }
        setSearchList(filteredList)
    }

    const getInitialList = ()=>{
        let filteredList = [];
        for (let i=0; i < 10 ; i++){
            filteredList.push(stocks[i])
        }
        setSearchList(filteredList)
    }
    
    useEffect(()=>{
        getInitialList()
    },[])

  return (
    <div className='searchBoxActive p-0 m-0'>
        <div>
        <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(event)=>handleOnChangeInput(event.target.value)}
            style={{width:"100%"}}
          />
        </div>
            {searchList && searchList.map((value)=>{
                return (<p className='p-1 m-0' onClick={()=>handleOnClickSearchItem(value)}>{value}</p>)
            })}
    </div>
  )
}