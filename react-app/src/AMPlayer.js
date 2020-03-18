import React from 'react'
import DSP from './dsp'
import Plot from 'react-plotly.js'

class AMPlayer extends React.Component {
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

    return (
      <div>
        <h1>AMPlayer</h1>
        <div>Amplitude = {this.state.a}</div>
        <div>Frequency = {this.state.f}</div>
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
              x: fx.slice(0, 2100/(this.state.sampleRate/this.state.bufferSize)),
              y: fy.slice(0, 2100/(this.state.sampleRate/this.state.bufferSize))
            }
          ]}
          layout={ {width: 640, height: 480, title: 'Frequency Domain'} }
        />
      </div>
    )
  }
}

export default AMPlayer
