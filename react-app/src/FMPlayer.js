import React from "react"
import DSP from "./dsp"
import Plot from 'react-plotly.js'

class FMPlayer extends React.Component {
  constructor() {
    super()
    this.state = {
      fArr: [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25],
      fIdx: 0, // Baseband Frequency
      fC: 1000, // Carrier Frequency
      fDev: 75, // FM Deviation
      bufferSize: 8192, // FFT
      sampleRate: 44100,
      numPoints: 1000,
    }
  }

  getTimeDomainData() {
    let _x = new Float64Array(this.state.sampleRate).fill(0)
    let _yD = new Float64Array(this.state.sampleRate).fill(0)
    let _yC = new Float64Array(this.state.sampleRate).fill(0)
    let _y = new Float64Array(this.state.sampleRate).fill(0)

    let f = this.state.fArr[this.state.fIdx]
    let fC = this.state.fC
    let fDev = this.state.fDev

    for (let i = 0; i < this.state.sampleRate; ++i) {
      _x[i] = i/this.state.sampleRate
      _yD[i] = Math.sin(2 * Math.PI * f * _x[i])
    }

    for (let i = 0; i < this.state.sampleRate; ++i) {
      _yC[i] = Math.sin(2 * Math.PI * fC * _x[i])
    }

    // y(t) = cos( 2*pi * f_c * t + ( f_dev / f_m ) * sin( 2*pi * f_m * t ) )
    for (let i = 0; i < this.state.sampleRate; ++i) {
      _y[i] = Math.cos(2 * Math.PI * fC * _x[i] + (fDev / f) * Math.sin(2 * Math.PI * f * _x[i]))
    }

    return ({
      x: _x,
      yD: _yD,
      yC: _yC,
      y: _y,
    })
  }

  handleClick(event) {
    if (event.target.id === "incf") {
      this.setState((prevState) => {
        return {
          fIdx: prevState.fIdx >= prevState.fArr.length - 1 ? prevState.fIdx : prevState.fIdx + 1
        }
      })
    } else if (event.target.id === "decf") {
      this.setState((prevState) => {
        return {
          fIdx: prevState.fIdx <= 0 ? prevState.fIdx : prevState.fIdx - 1
        }
      })
    } else if (event.target.id === "incfc") {
      this.setState((prevState) => {
        return {
          fC: prevState.fC >= 2000 ? prevState.fC : prevState.fC + 100
        }
      })
    } else if (event.target.id === "decfc") {
      this.setState((prevState) => {
        return {
          fC: prevState.fC <= 400 ? prevState.fC : prevState.fC - 100
        }
      })
    } else if (event.target.id === "incfdev") {
      this.setState((prevState) => {
        return {
          fDev: prevState.fDev >= 200 ? prevState.fDev : prevState.fDev + 25
        }
      })
    } else if (event.target.id === "decfdev") {
      this.setState((prevState) => {
        return {
          fDev: prevState.fDev <= 0 ? prevState.fDev : prevState.fDev - 25
        }
      })
    }
  }

  stopAudio() {
    // console.log(window.AudioContext)
  }

  startAudio() {
    var arr = this.getTimeDomainData().y
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    var context = new AudioContext();
    var buf = new Float32Array(arr.length)
    for (var i = 0; i < arr.length; i++) buf[i] = arr[i]
    var buffer = context.createBuffer(1, buf.length, context.sampleRate)
    buffer.copyToChannel(buf, 0)
    var source = context.createBufferSource();
    source.buffer = buffer;
    source.connect(context.destination);
    source.start(0);
  }

  playAudio() {
    // this.stopAudio();
    this.startAudio();
  }

  render() {
    var timeData = this.getTimeDomainData()
    var fft = new DSP.FFT(this.state.bufferSize, this.state.sampleRate)
    fft.forward(timeData.y.slice(0, this.state.bufferSize))
    var fy = fft.spectrum
    var fx = Array(fy.length).fill(0)

    for (let i = 0; i < fx.length; ++i) {
      fx[i] = this.state.sampleRate / this.state.bufferSize * i
      // fy[i] = fy[i] * -1 * Math.log((fft.bufferSize/2 - i) * (0.5/fft.bufferSize/2)) * fft.bufferSize
    }

    var fmax = 2625

    return (
      <div className="app-container">
        <div className="row text-center app-row">
          <div className="col-md text-center">
            <div className="text-data">Baseband Frequency(Hz)<br/>{this.state.fArr[this.state.fIdx]}</div>
            <button id="incf" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>+</button>
            <button id="decf" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>-</button>
          </div>
          <div className="col-md text-center">
            <div className="text-data">Carrier Frequency(Hz)<br/>{this.state.fC}</div>
            <button id="incfc" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>+</button>
            <button id="decfc" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>-</button>
          </div>
          <div className="col-md text-center">
            <div className="text-data">FM Deviation(Hz)<br/>{this.state.fDev}</div>
            <button id="incfdev" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>+</button>
            <button id="decfdev" type="button" className="btn btn-dark" onClick={event => this.handleClick(event)}>-</button>
          </div>
        </div>
        <div className="row text-center app-row">
          <div className="col-sm text-center">
            <button className="btn btn-dark" onClick={event => this.playAudio(event)}>
              <div className="text-btn">play</div>
            </button>
          </div>
        </div>
        <div className="row text-center app-row">
          <div className="col-md text-center">
            <Plot
              data={[
                {
                  x: timeData.x.slice(0, this.state.numPoints-1),
                  y: timeData.yD.slice(0, this.state.numPoints-1),
                }
              ]}
              layout={ {width: 480, height: 320, title: 'Data Wave (Time Domain)', yaxis: {range: [-1, 1]}, margin: 0} }
            />
          </div>
          <div className="col-md text-center">
            <Plot
              data={[
                {
                  x: timeData.x.slice(0, this.state.numPoints-1),
                  y: timeData.yC.slice(0, this.state.numPoints-1),
                }
              ]}
              layout={ {width: 480, height: 320, title: 'Carrier Wave (Time Domain)', yaxis: {range: [-1, 1]}, margin: 0} }
            />
          </div>
          <div className="col-md text-center">
            <Plot
              data={[
                {
                  x: timeData.x.slice(0, this.state.numPoints-1),
                  y: timeData.y.slice(0, this.state.numPoints-1),
                }
              ]}
              layout={ {width: 480, height: 320, title: 'FM Wave (Time Domain)', yaxis: {range: [-2, 2]}, margin: 0} }
            />
          </div>
          <div className="col-md text-center">
            <Plot
              data={[
                {
                  x: fx.slice(0, fmax/(this.state.sampleRate/this.state.bufferSize)),
                  y: fy.slice(0, fmax/(this.state.sampleRate/this.state.bufferSize))
                }
              ]}
              layout={ {width: 480, height: 320, title: 'FM Wave (Frequency Domain)', margin: 0} }
            />
          </div>
        </div>
      </div>
    )
  }
}

export default FMPlayer
