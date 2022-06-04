import React from 'react';
import { Link } from "react-router-dom";

// Components
import Title from '../components/Title';

// Bootstrap
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import {Navbar,Nav,NavDropdown} from 'react-bootstrap'
// import Nav from 'react-bootstrap/Navbar'

// Fontawesome
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlay } from '@fortawesome/free-solid-svg-icons'

import Img from '../images/graphic_model.PNG'

import { useCookies } from 'react-cookie'
import ParticlesBg from 'particles-bg'

import '../components/scss/button.css'
import FocoNavbar from '../components/FocoNavbar';
import ThreeJSCanvas from '../components/ThreeJSCanvas';

function MeetFoco() {
    const [cookies, setCookie] = useCookies(['logged_user'])
    console.log("cookies: " + cookies.logged_user)
  return (
    <>
    <div className='particlesBG'>
      <ParticlesBg className="particles-bg-canvas-self" type="cobweb" bg={true} color="#DADADA" height={'100%'}/>
    </div>
    <div style={{ padding: '1%' }}>
    <Container>
      <FocoNavbar goesBack={false} hasLoginBtn={true} cookies={cookies} setCookie={setCookie}/>
    </Container>

    <h2 className='titleH3'>Meet FoCo</h2>

    <Container>
        <Row style={{marginTop:'5%'}}>
            <Col>
                <Row>
                    <Col style={{paddingLeft:'5%',paddingRight:'5%'}}>
                        <ThreeJSCanvas/>
                    </Col>
                </Row>
                <Row style={{marginTop:'5%',width:'100%',textAlign:'center',paddingLeft:'5%',paddingRight:'5%'}}>
                    <Col style={{marginBottom:'5%'}}>
                        <Button>Calm</Button>
                    </Col>
                    <Col style={{marginBottom:'5%'}}>
                        <Button>Energetic</Button>
                    </Col>
                    <Col style={{marginBottom:'5%'}}>
                        <Button>Agressive</Button>
                    </Col>
                    <Col style={{marginBottom:'5%'}}>
                        <Button>Friendly</Button>
                    </Col>
                </Row>
            </Col>
            <Col className='meetFocoDescription' style={{marginLeft:'5%',marginRight:'5%'}}>
                <Row>
                <p className='meetFocoP'>
                    Hi! I'm Foco, the Football Commentator Mascot.
                    <br/>I was created to comment my friends' games to you.
                    You can play with my emotions with the buttons below me.
                    <br/>Don't overuse it tho, because even though I'm a robot I still have feelings :(
                </p>
                </Row>
            </Col>
        </Row>
    </Container>

    </div>
    </>
  )
}

export default MeetFoco