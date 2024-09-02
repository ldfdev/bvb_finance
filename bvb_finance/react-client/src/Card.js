import './Card.css';

function Card(props){
    return (
        <div className="card">
            <h2>{props.ticker}</h2>
            <p>Date {props.date}</p>
            <p>Quantity {props.quantity}</p>
            <p>Price {props.price}</p>
        </div>
    )
}
export default Card