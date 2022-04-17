import React from 'react'
import { Row,Col } from 'react-bootstrap'
import '../components/components_css/Statistics.css';

function StatisticLine({paramA,condition,paramB}) {
  return (
    <Row>
        <Col>
            <h3>{paramA}</h3>
        </Col>
        <Col>
            <p>{condition}</p>
        </Col>
        <Col>
            <h3>{paramB}</h3>
        </Col>
    </Row>
  )
}

export default StatisticLine