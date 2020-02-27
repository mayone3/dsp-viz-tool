var pi = 3.1415926535897932384626
var samplerate = 44100.0
var duration = 1.0
var a = 1.0
var f = 440.0
var n = nj.arange(samplerate * duration, 'float64')
var t = n.divide(samplerate)

// sample = A * sin(2 * pi * f * t)
var sample = nj.sin(t.multiply(2*pi*f))

console.log(samplerate.toString())
console.log(duration.toString())
console.log(a.toString())
console.log(f.toString())
console.log(n.toString())
console.log(t.toString())
console.log(sample.toString())
