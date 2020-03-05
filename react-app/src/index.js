import React from "react"
import ReactDOM from "react-dom"

import DSP from "./dsp"
import AMPlayer from "./AMPlayer"
import FMPlayer from "./AMPlayer"
import FixedFreqPlayer from "./FixedFreqPlayer"
import MultiFreqPlayer from "./MultiFreqPlayer"

class App extends React.Component {
  constructor() {
    super()
    this.state = {
      currentRunningApp: 'AMPlayer'
    }
  }

  getCurrentRunningApp() {
    if (this.state.currentRunningApp === 'FixedFreqPlayer') {
      return <FixedFreqPlayer />
    } else if (this.state.currentRunningApp === 'MultiFreqPlayer') {
      return <MultiFreqPlayer />
    } else if (this.state.currentRunningApp === 'AMPlayer') {
      return <AMPlayer />
    } else if (this.state.currentRunningApp === 'FMPlayer') {
      return <FMPlayer />
    } else {
      return <div>DO SOMETHING</div>
    }
  }

  render() {
    return this.getCurrentRunningApp();
  }
}

ReactDOM.render(
  <App />,
  document.getElementById("root")
);
