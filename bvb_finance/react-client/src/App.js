import React , {useState, useEffect} from 'react'

function App() {
  //initiali state of the variable backendData is the list consisting of "A", "B", "C"
  const [backendData, setDataFunction] = useState(["A", "B", "C"])

  useEffect(() => {
    fetch("/api/financial_reports/portfolio_tickers/").then(
      res => res.json()
    ).then(
      fetchedData => {
        // next backendData is assigned the value of fetchedData
        // but the modification in not visivle inside the scope of this function
        setDataFunction(fetchedData)
        console.log("Backend data", fetchedData)
        fetchedData.map( (ticker, i) => (
          console.log("Iteration", i, ticker, "typeof", typeof ticker)
        ))
      }
    )
  },[])
  return (
    <div>
      {
        backendData.map( (ticker, i) => (
          <p key={i}> {JSON.stringify(ticker)} </p>
        ))
      }
    </div>
  )
}

export default App