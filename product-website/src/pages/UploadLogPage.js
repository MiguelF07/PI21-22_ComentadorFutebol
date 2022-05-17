import React, { useState, useRef, useEffect } from 'react'
import Title from '../components/Title'
import DragDrop from '../components/DragDrop'
import { Container } from 'react-bootstrap'
import { Row } from 'react-bootstrap'
import { Col } from 'react-bootstrap'
import Img from '../images/upload.jpeg'
import { Button } from 'react-bootstrap'
import '../components/components_css/Form.css';
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
import Spinner from 'react-bootstrap/Spinner'
import ParticlesBg from 'particles-bg'
import FocoNavbar from '../components/FocoNavbar';

import { useCookies } from 'react-cookie'
import axios from 'axios'
import TTS from '../components/TTS'

function UploadLogPage() {

  const [cookies, setCookie] = useCookies(['logged_user'])
  // const inputFile = useRef(null)

  const [file, setFile] = useState(null)

  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [privacy, setPrivacy] = useState("Private")

  const [loading, setLoading] = useState(false)

  // tts states
  const [tts, setTts] = useState(new TTS())
  const [hasLoadedVoices, setHasLoadedVoices] = useState(false)
  let hasButtonClicked = {value: false}

  console.log("title: " + title)
  console.log("description: " + description)
  console.log("privacy: " + privacy)

  useEffect(() => {
    if (!tts.isSearchingVoices) {
      tts.updateStateWhenVoicesLoaded(setHasLoadedVoices)
    }
  }, [])

  useEffect(() => {
    console.log("loaded voices", tts.voices)
    const lang_voices = tts.getVoicesByLanguage("en")
    const voices_names = tts.getVoicesByName("male", lang_voices)
    tts.setVoice(voices_names[0])
  }, [hasLoadedVoices])

  function processFile() {
    if (file) {

      console.log("yup")
      tts.speak("We are starting the convertion, please wait.", hasButtonClicked) // its necessary to create the initial speak
      // const url = 'http://127.0.0.1:8000/file_upload/';
      const url = 'http://127.0.0.1:8000/chunk_upload/';
      const formData = new FormData();
      formData.append('file', file);
      formData.append('fileName', title);
      formData.append('fileDescription', description);
      formData.append('filePrivacy', privacy);

      let fr = new FileReader()
      fr.onload = () => {
        // console.log("file text", fr.result)
        // Post used only for simulation test
        // formData.append("simulator", fr.result)
        const testssss = ["sus", "amogus", "rel"]
        formData.append("simulator", JSON.stringify(testssss))
        // for (let i = 0; i < testssss.length; i++) {
        //   formData.append("simulator[]", testssss[i])
        // }

        axios.post(url, formData, config).then((response) => {
          console.log("response", response)
          // let data = response.data
          // console.log(data);
          
          // for (let i = 0; i < 5; i++) {
          //   tts.emmitAudio(data[i].text, hasButtonClicked)
          // }
          
          // document.getElementById('confirmBtn').disabled = false;
          // setLoading(false)


          // document.getElementById('confirmBtn').innerHTML = "Confirm";
        });
      }

      fr.readAsText(file)

      const config = {
        headers: {
          'content-type': 'multipart/form-data',
          // 'Access-Control-Allow-Origin': 'http://localhost:3001'
        },
      };
      document.getElementById('confirmBtn').disabled = true;
      const spinner = "<Spinner animation=\"border\" role=\"status\"><span className=\"visually-hidden\">Loading...</span></Spinner>";
      {/* <Spinner animation="border" role="status"><span className="visually-hidden">Loading...</span></Spinner> */ }
      // document.getElementById('confirmBtn').innerHTML = spinner;
      setLoading(true)

      /* True post
      axios.post(url, formData, config).then((response) => {
        let data = response.data
        console.log(data);
        
        for (let i = 0; i < 5; i++) {
          tts.emmitAudio(data[i].text, hasButtonClicked)
        }
        
        document.getElementById('confirmBtn').disabled = false;
        setLoading(false)


        // document.getElementById('confirmBtn').innerHTML = "Confirm";
      });
      */

    }
    else {
      console.log("NO FILE!!!")
    }
  }

  function handleCallback(file, filename) {
    setFile(file);
    setTitle(filename);
  }

  // const onButtonClick = () => {
  //   inputFile.current.click()
  // }

  return (<>
      <div className='particlesBG'>
      <ParticlesBg className="particles-bg-canvas-self" type="cobweb" bg={true} color="#DADADA"/>
      </div>
      <div style={{ padding: '1%' }}>
      <Container>
        <FocoNavbar goesBack={true} backPage="/select_game" hasLoginBtn={true} cookies={cookies} setCookie={setCookie}/>
      </Container>

      <Container>
        <Row>
          <Col>
            <Title title="FoCo" subtitle="Upload Your Log File"></Title>
          </Col>
        </Row>
      </Container>

      <Container>
        <Col style={{ marginLeft: '10%', marginRight: '10%' }}>

          <Row style={{ marginTop: '5%', marginBottom: '5%', display: 'flex', justifyContent: 'center'}}>
            <DragDrop parentCallback={handleCallback} />
          </Row>

          {/* <Row style={{ textAlign: 'center' }}>
            <input type='file' id='file' ref={inputFile} style={{ display: 'none' }} onChange={(event) => {
              setFile(event.target.files[0])
              setTitle(event.target.files[0].name)
              document.getElementById('confirmBtn').disabled = false
            }} />
          </Row> */}

          {file ?
            <Row style={{ marginBottom: '5%' }}>
              <Col style={{paddingLeft:'20%',paddingRight:'20%'}}>
              <Container className='logUpload'>
              <Form>

                <Form.Group className="mb-3">
                  <Form.Label>Title</Form.Label>
                  <Form.Control type="text" placeholder="Enter title" defaultValue={file.name} onChange={(e) => { setTitle(e.target.value) }} />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <FloatingLabel label="Comments">
                    <Form.Control
                      as="textarea"
                      placeholder="Enter Description"
                      style={{ height: '100px' }}
                      onChange={(e) => { setDescription(e.target.value) }}
                    />
                  </FloatingLabel>
                </Form.Group>

                <Form.Group>
                  <Form.Label>Video Privacy</Form.Label>
                  <FloatingLabel>
                    <Form.Select style={{ paddingTop: '0px', paddingBottom: '0px', height: '40px' }} onChange={(e) => { setPrivacy(e.target.value) }}>
                      <option value="Private">Private</option>
                      <option value="Public">Public</option>
                    </Form.Select>
                  </FloatingLabel>
                </Form.Group>

                <Form.Group style={{ textAlign: 'center', marginTop: '5%' }}>
                  <Button className='btnUpload' type="button" variant="primary" size="lg" style={{ width: '18%', margin: 'auto' }}  onClick={processFile}>
                    {loading ?
                      <Spinner animation="border" role="status"><span className="visually-hidden">Loading...</span></Spinner>
                      :
                      "Confirm"
                    }
                  </Button>
                </Form.Group>

              </Form>
              </Container>
              </Col>
            </Row>
            :
            <></>}

          {/* <Row>
            <Button variant="primary" type="submit" size="lg" style={{ width: '18%', margin: 'auto' }} className="formBtn" onClick={onButtonClick}>
              Load
            </Button>
          </Row> */}

        </Col>
      </Container>
    </div>
    </>
  )
}

export default UploadLogPage