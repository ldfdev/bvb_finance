import React , {useState, useEffect, useRef} from 'react'
import Card from './Card'
import './Card.css';

function App() {
  //initiali state of the variable backendData is the list consisting of "A", "B", "C"
  const [backendData, setDataFunction] = useState(["A", "B", "C"])

  const [scrollPosition, setScrollPosition] = useState(0);

  const handleScroll = (scrollAmount) => {
    // Source
    // https://timetoprogram.com/horizontal-scrolling-component-with-buttons-react/
    // Calculate the new scroll position
    const newScrollPosition = scrollPosition + scrollAmount;
  
    // Update the state with the new scroll position
    setScrollPosition(newScrollPosition);
  
    // Access the container element and set its scrollLeft property
    containerRef.current.scrollLeft = newScrollPosition;
  };

  const containerRef = useRef();

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
    // all card are displayed ona  single row
    <div className='containerDiv'>
      <div className='divButton'>
        <button className='scrollButton' onClick={() => handleScroll(-200)}>Scroll Left</button>
      </div>
      <div className='cardsHolder' ref={containerRef}>
        {
          backendData.map( (ticker, i) => (
            <Card></Card>
          ))
        }
      </div>
      <div className='divButton'>
        <button className='scrollButton' onClick={() => handleScroll(200)}>Scroll Right</button>
      </div>
   </div>
  )
}

export default App