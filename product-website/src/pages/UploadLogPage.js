import React from 'react'
import Title from '../components/Title'
import { Container } from 'react-bootstrap'
import { Row } from 'react-bootstrap'
import { Col } from 'react-bootstrap'
import Img from '../images/upload.jpeg'
import { Button } from 'react-bootstrap'
import '../components/components_css/Form.css';

function UploadLogPage() {
  return (
    <>
    <Title title='Commentator' subtitle="Upload your Log File" />
    <Container>
        <Col style={{marginLeft:'10%',marginRight:'10%'}}>
        <Row style={{marginTop:'5%',marginBottom:'5%'}}>
        <img
        alt='Field'
        src={Img}
        className='img-thumbnail'
        />
        </Row>
        <Row style={{marginBottom:'10%',textAlign:'center'}}>
            <Button variant="primary" type="submit" size="lg" style={{width:'18%',margin:'auto'}}>
                Load
            </Button>
        </Row>
        </Col>
    </Container>
    </>
  )
}

export default UploadLogPage