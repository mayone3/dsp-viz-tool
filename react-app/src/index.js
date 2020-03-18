import React from "react"
import ReactDOM from "react-dom"

import DSP from "./dsp"
import AMPlayer from "./AMPlayer"
import FMPlayer from "./FMPlayer"
import FixedFreqPlayer from "./FixedFreqPlayer"
import MultiFreqPlayer from "./MultiFreqPlayer"

class App extends React.Component {
  constructor() {
    super()
    this.state = {
      appList: [
        'FixedFreqPlayer',
        'MultiFreqPlayer',
        'AMPlayer',
        'FMPlayer',
      ],
      currApp: 0
    }
  }

  getCurrApp() {
    if (this.state.appList[this.state.currApp] === 'FixedFreqPlayer') {
      return <FixedFreqPlayer />
    } else if (this.state.appList[this.state.currApp] === 'MultiFreqPlayer') {
      return <MultiFreqPlayer />
    } else if (this.state.appList[this.state.currApp] === 'AMPlayer') {
      return <AMPlayer />
    } else if (this.state.appList[this.state.currApp] === 'FMPlayer') {
      return <FMPlayer />
    } else {
      return <div>ERROR</div>
    }
  }

  handleClick() {
    this.setState((prevState) => {
      let nextApp = (prevState.currApp + 1) % (prevState.appList.length)
      return {
        currApp: nextApp
      }
    });
  }

  render() {
    return (
      <div>
        <link
          rel="stylesheet"
          href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css"
          integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4"
          crossOrigin="anonymous"
        />
        <div>Current App is {this.state.appList[this.state.currApp]}</div>
        <button onClick={() => this.handleClick()}>NEXT</button>
        {this.getCurrApp()}
      </div>
    )
  }
}

ReactDOM.render(
  <App />,
  document.getElementById("root")
);
