import React from "react"
import DSP from "./dsp"
import Plot from 'react-plotly.js'

class MultiFreqPlayer extends React.Component {
  constructor() {
    super()
    this.state = {
      a: [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
      f: [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25],
      bufferSize: 8192,
      sampleRate: 44100,
      numPoints: 1000,
    }
  }

  getTimeDomainData() {
    let _x = new Float64Array(this.state.sampleRate).fill(0)
    let _y = new Float64Array(this.state.sampleRate).fill(0)

    for (let i = 0; i < this.state.sampleRate; ++i) {
      _x[i] = i/this.state.sampleRate
      for (let freqIndex = 0; freqIndex < this.state.f.length; ++freqIndex) {
        _y[i] += this.state.a[freqIndex] * Math.sin(2 * Math.PI * this.state.f[freqIndex] * _x[i])
      }
    }

    let r = Math.max(Math.abs(Math.max(..._y)), Math.abs(Math.min(..._y)))

    for (let i = 0; i < _y.length; ++i) {
      _y[i] /= r
    }

    return ({
      x: _x,
      y: _y
    })
  }

  handleChange(event) {
    let id = event.target.id.slice(10)
    let _a = this.state.a
    _a[id] = event.target.value

    this.setState({
      a: _a
    })
    
    this.playAudio()
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
    let timeData = this.getTimeDomainData()
    let fft = new DSP.FFT(this.state.bufferSize, this.state.sampleRate)
    fft.forward(timeData.y.slice(0, this.state.bufferSize))
    var fy = fft.spectrum
    var fx = Array(fy.length).fill(0)

    for (let i = 0; i < fx.length; ++i) {
      fx[i] = this.state.sampleRate / this.state.bufferSize * i
      // fy[i] = fy[i] * -1 * Math.log((fft.bufferSize/2 - i) * (0.5/fft.bufferSize/2)) * fft.bufferSize
    }

    var fmax = 825

    return (
      <div>
        <h1>MultiFreqPlayer</h1>
        <div className="row justify-content-center">
          <div className="col-sm">
            <input id="multifreq-0" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[0]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-1" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[1]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-2" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[2]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-3" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[3]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-4" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[4]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-5" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[5]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-6" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[6]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-7" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[7]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-8" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[8]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-9" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[9]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-10" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[10]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-11" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[11]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
          <div className="col-sm">
            <input id="multifreq-12" className="custom-range no-border" type="range" onChange={event => this.handleChange(event)} value={this.state.a[12]} min="0.0" max="1.0" step="0.1" orientation="vertical" />
          </div>
        </div>
        <div className="row justify-content-center">
          <button onClick={event => this.playAudio(event)}>PLAY AUDIO</button>
        </div>
        <div className="row justify-content-center">
          <div className="col-sm">
            <Plot
              data={[
                {
                  x: timeData.x.slice(0, this.state.numPoints-1),
                  y: timeData.y.slice(0, this.state.numPoints-1),
                }
              ]}
              layout={ {width: 640, height: 480, title: 'Time Domain'} }
            />
          </div>
          <div className="col-sm">
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
        </div>
      </div>
    )
  }
}

export default MultiFreqPlayer
