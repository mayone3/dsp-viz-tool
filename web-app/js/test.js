// import React
// import ReactDOM

import AMPlayer from "./AMPlayer.js"

ReactDOM.render(<AMPlayer />, document.getElementById("root"))

// var pi = 3.1415926535897932384626
// var samplerate = 44100.0
// var duration = 1.0
// var a = 1.0
// var f = 440.0
// var numPoints = 250
// var n = nj.arange(samplerate * duration, 'float64')
// var t = n.divide(samplerate)
//
// // sample = A * sin(2 * pi * f * t)
// var sample = nj.sin(t.multiply(2*pi*f))
//
// console.log(samplerate.toString())
// console.log(duration.toString())
// console.log(a.toString())
// console.log(f.toString())
// console.log(n.toString())
// console.log(t.toString())
// console.log(sample.toString())
//
// var sampleFrequencyDomainPlot = document.getElementById('sample-frequency-domain-plot');
// var sampleFrequencyDomainData = [{
//     x: t.tolist().slice(0,numPoints),
//     y: sample.tolist().slice(0,numPoints)
// }]
// var sampleFrequencyDomainLayout = {
//     yaxis: {
//         range: [-1.1, 1.1]
//     },
//     margin: {
//         t: 0
//     }
// }
//
// Plotly.newPlot(
//     sampleFrequencyDomainPlot,
//     sampleFrequencyDomainData,
//     sampleFrequencyDomainLayout
// );
