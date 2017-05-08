const fs = require('fs')
const bluebird = require('bluebird')
const Rx = require('rxjs')
const log = require('single-line-log').stdout

const readAsync = bluebird.promisify(fs.readFile)

const readFile$ = Rx.Observable.create(async (observer) => {
  const file = await readAsync('../iris.csv', 'utf8')
  const rows = file.split('\n').filter(v => v)
  const length = rows.length
  rows.forEach((row => setTimeout(() => observer.next({ row, length }))))
  setTimeout(() => observer.complete())
})

const transformRow$ = readFile$
  .map(({ row, length }) => ({ row: row.split(','), length }))
  .map(({ row, length }) => ({ inputs: row.slice(0, -1), iris: row[0], length }))

const getInputObject = (input, rId) => input
  ? { ...input, rConnections: [...input.rConnections, rId] }
  : { rConnections: [rId] }

const rConnections$ = transformRow$
  .scan((graph, { length, inputs }, rId) => ({
    ...graph,
    params: {
      ...graph.params,
      ...inputs.reduce((acc, curr, i) => ({
        ...acc,
        [i]: {
          ...graph.params[i],
          ...(acc[i] || {}),
          [curr]: getInputObject((graph.params[i] || {})[curr], rId)
        }
      }), {})
    },
    counter: graph.counter + 1,
    length
  }), { params: {}, counter: 0, text: 'Calculating R connections:' })

const paramsSplitter$ = rConnections$
  .filter(({ counter, length }) => counter === length)
  .map(({ params }) => Rx.Observable.create(async (observer) => {
    const paramsKeys = Object.keys(params)
    const length = paramsKeys.length
    paramsKeys.forEach(key => setTimeout(() => {
      const inputs = Object.keys(params[key])
      const maxMinDiff = Math.max(...inputs) - Math.min(...inputs)
      observer.next({ key, inputs, maxMinDiff, length })
    }))
    setTimeout(() => observer.complete())
  }))
  .flatMap(Rx.Observable.from)

const weights$ = paramsSplitter$
  .scan((graph, { key, inputs, maxMinDiff, length }) => ({
    ...graph,
    weights: {
      ...graph.weights,
      [key]: {
        ...graph.weights[key],
        ...inputs.slice().sort((a, b) => a - b).reduce((acc, id) => ({
          ...acc,
          obj: {
            ...acc.obj,
            ...(
              acc.lastItem !== undefined
                ? { [`${acc.lastItem}|${id}`]: (id - acc.lastItem) / maxMinDiff }
                : {}
            )
          },
          lastItem: id
        }), { obj: {}, lastItem: undefined }).obj
      }
    },
    d: inputs,
    counter: graph.counter + 1,
    length
  }), { weights: {}, counter: 0, text: 'Calculating weights:' })

const createGraph$ = weights$
  .combineLatest(rConnections$, (weights, rConnections) => ({ weights, rConnections }))
  .filter(({ weights, rConnections }) => (
    weights.counter === weights.length && rConnections.counter === rConnections.length
  ))
  .map(({ weights: { weights }, rConnections: { params } }) => Rx.Observable.create(async (observer) => {
    await new Promise(resolve => setTimeout(resolve))
    observer.next({ params, weights })
    observer.complete()
  }))
  .flatMap(Rx.Observable.from)

const progress$ = Rx.Observable.merge(rConnections$, weights$)
  .map(({ text, counter, length }) => ({ text, progress: Math.floor(100 * counter / length) }))

progress$.subscribe({
  next: ({ text, progress }) => {
    log(`${text} progress ${progress}%`)
    if (progress === 100) {
      console.log()
    }
  },
  error: err => console.error('something wrong occurred: ' + err),
  complete: () => console.log(),
})

createGraph$.subscribe({
  // next: graph => console.log(JSON.stringify(graph)),
  complete: () => console.log('Task completed')
})
