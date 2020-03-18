import React from "react"
import DSP from "./dsp"
import Plot from 'react-plotly.js'

class FixedFreqPlayer extends React.Component {
  constructor() {
    super()
    this.state = {
      a: 1.0,
      f: 440.0,
      bufferSize: 8192,
      sampleRate: 44100,
      numPoints: 1000,
    }
  }

  getTimeDomainData() {
    var _x = new Float64Array(this.state.sampleRate).fill(0)
    var _y = new Float64Array(this.state.sampleRate).fill(0)

    for (let i = 0; i < this.state.sampleRate; ++i) {
      _x[i] = i/this.state.sampleRate
      _y[i] = this.state.a * Math.sin(2 * Math.PI * this.state.f * _x[i])
    }

    return ({
      x: _x,
      y: _y
    })
  }

  handleClick(event) {
    if (event.target.id === "inca") {
      this.setState((prevState) => {
        return {
          a: prevState.a >= 0.9 ? prevState.a : prevState.a + 0.1
        }
      })
    } else if (event.target.id === "deca") {
      this.setState((prevState) => {
        return {
          a: prevState.a <= 0.1 ? prevState.a : prevState.a - 0.1
        }
      })
    } else if (event.target.id === "incf") {
      this.setState((prevState) => {
        return {
          f: prevState.f >= 4000 ? prevState.f : Math.round(prevState.f * 1.1)
        }
      })
    } else if (event.target.id === "decf") {
      this.setState((prevState) => {
        return {
          f: prevState.f <= 20 ? prevState.f : Math.round(prevState.f / 1.1)
        }
      })
    }
  }

  playAudio() {
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

    var fmax = Math.max(2000, this.state.f) * 1.1

    return (
      <div>
        <h1>FixedFreqPlayer</h1>
        <div>Amplitude = {this.state.a.toFixed(1)}
          <button id="inca" type="button" onClick={event => this.handleClick(event)}>+</button>
          <button id="deca" type="button" onClick={event => this.handleClick(event)}>-</button>
        </div>
        <div>Frequency = {this.state.f}
          <button id="incf" type="button" onClick={event => this.handleClick(event)}>+</button>
          <button id="decf" type="button" onClick={event => this.handleClick(event)}>-</button>
        </div>
        <button onClick={event => this.playAudio(event)}>PLAY</button>
        <Plot
          data={[
            {
              x: timeData.x.slice(0, this.state.numPoints-1),
              y: timeData.y.slice(0, this.state.numPoints-1),
            }
          ]}
          layout={ {width: 640, height: 480, title: 'Time Domain'} }
        />
        <Plot
          data={[
            {
              x: fx.slice(0, fmax/(this.state.sampleRate/this.state.bufferSize)),
              y: fy.slice(0, fmax/(this.state.sampleRate/this.state.bufferSize))
            }
          ]}
          layout={ {width: 640, height: 480, title: 'Frequency Domain'} }
        />
      </div>
    )
  }
}

export default FixedFreqPlayer
