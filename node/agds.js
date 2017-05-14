const fs = require('fs')
const bluebird = require('bluebird')
const Rx = require('rxjs')
const log = require('single-line-log').stdout

const readAsync = bluebird.promisify(fs.readFile)

const transformData = (value) => {
  const data = {
    'Iris-setosa': 1,
    'Iris-versicolor': 2,
    'Iris-virginica': 3
  }
  return data[value] || value
}

const input$ = Rx.Observable.of(127).share()

const readFile$ = Rx.Observable.create(async (observer) => {
  const file = await readAsync('../iris.csv', 'utf8')
  const rows = file.split('\n').filter(v => v)
  observer.next(rows)
}).share()

const assignRConnections = mayBeUndef::((input, rId) =>
  ({ ...input, rConnections: [...(input.rConnections || []), rId] })
)

const params$ = readFile$
  .flatMap(rows => {
    const length = rows.reduce((acc, row) => acc + row.split(',').length, 0)
    return Rx.Observable.create((observer) => {
      setTimeout(() => rows.forEach(row => {
        row.split(',').map(transformData).forEach((curr, i) => observer.next({ curr, i }))
      }))
      // observer.complete()
    })
      .scan((graph, { curr, i }, rId) => ({
        ...graph,
        params: {
          ...graph.params,
          [i]: {
            ...graph.params[i],
            [curr]: assignRConnections(mayBeUndef::graph.params[i][curr], rId)
          }
        },
        counter: graph.counter + 1
      }), { params: {}, counter: 0, length, text: 'Calculating R connections:' })
    }
  )
  .share()

const assignConnections = (acc, key, id, prev, next) => ({
  [id]: {
    ...acc.params[key][id],
    connections: {
      ...acc.params[key][id].connections,
      ...(prev ? { prev } : {}),
      ...(next ? { next } : {})
    }
  }
})

const weights$ = params$
  .filter(({ counter, length }) => counter === length)
  .flatMap(graph => {
    const { params } = graph
    const paramsKeys = Object.keys(params)
    const length = Object.keys(paramsKeys).reduce((acc, key) => acc + Object.keys(params[key]).length, 0)
    return Rx.Observable.create((observer) => {
      setTimeout(() => paramsKeys.forEach(key => {
        const inputs = Object.keys(params[key])
        const maxMinDiff = Math.max(...inputs) - Math.min(...inputs)
        let lastItem = undefined
        inputs.slice().sort((a, b) => a - b).forEach(id => {
          observer.next({ key, id, lastItem, maxMinDiff })
          lastItem = id
        })
      }))
      // observer.complete()
    })
      .scan(mayBeUndef::((graph, { key, id, lastItem, maxMinDiff }) => ({
        ...graph,
        weights: {
          ...graph.weights,
          [key]: {
            ...graph.weights[key],
            ...lastItem !== undefined ? {[`${lastItem}|${id}`]: 1 - ((id - lastItem) / maxMinDiff)} : {}
          }
        },
        params: {
          ...graph.params,
          [key]: {
            ...graph.params[key],
            ...assignConnections(graph, key, id, lastItem),
            ...(
              lastItem
                ? assignConnections(graph, key, lastItem, null, id)
                : {}
            )
          }
        },
        counter: graph.counter + 1
      })), { ...graph, counter: 0, length, text: 'Calculating weights:' })
  })
  .share()

const createGraph$ = weights$
  .filter(({ counter, length }) => counter === length)
  .map(({ params, weights }) => ({ params, weights }))

const getXValue = (graph, index, input, id) => {
  const greater = id > input
  const second = greater
    ? graph.params[index][id].connections.prev
    : graph.params[index][id].connections.next
  const secondX = graph.x[index][second]
  const weightId = greater ? `${second}|${id}` : `${id}|${second}`
  const weight = graph.weights[index][weightId]
  return secondX * weight
}

const xValues$ = Rx.Observable.combineLatest(createGraph$, input$, readFile$)
  .flatMap(([graph, input, rows]) => {
    const inputs = rows[input].split(',').map(transformData)
    const initX = Object.keys(graph.params).reduce((acc, key, i) => ({
      ...acc,
      [key]: {
        [inputs[i]]: 1
      }
    }), {})
    const length = Object
      .keys(graph.params)
      .reduce((acc, key) => acc + Object.keys(graph.params[key]).length - 1, 0)

    return Rx.Observable.create((observer) => {
      setTimeout(() => inputs.forEach((rowInput, i) => {
        const path = []
        let next = graph.params[i][rowInput].connections.next
        let prev = graph.params[i][rowInput].connections.prev
        while (next || prev) {
          if (next) {
            const id = next
            observer.next({ id, input: rowInput, index: i, length })
            next = graph.params[i][next].connections.next
          }
          if (prev) {
            const id = prev
            observer.next({ id, input: rowInput, index: i, length })
            prev = graph.params[i][prev].connections.prev
          }
        }
      }))
    })
      .scan(((graph, { id, input, index }) => ({
        ...graph,
        x: {
          ...graph.x,
          [index]: {
            ...graph.x[index],
            [id]: getXValue(graph, index, input, id)
          }
        },
        input,
        counter: graph.counter + 1,
      })), { ...graph, x: initX, counter: 0, length, text: `Calculating x values for input ${input}:` })
  })
  .share()

const r$ = Rx.Observable.combineLatest(xValues$, readFile$)
  .filter(([{ counter, length }]) => counter === length)
  .map(([{ params, weights, x }, rows]) => ({ graph: { params, weights, x }, rows }))
  .flatMap(({ graph, rows }) => {
    const length = rows.length
    const coeff = 1 / rows[0].split(',').length
    return Rx.Observable.create((observer) => {
      setTimeout(() => rows.forEach((row, i) => {
        const similarity = row.split(',').map(transformData).reduce((acc, item, j) => {
          return acc + coeff * graph.x[j][item]
        }, 0)
        observer.next({ similarity, index: i })
      }))
    })
      .scan((acc, { similarity, index }) => ({
        ...acc,
        similarities: {
          ...acc.similarities,
          [index]: similarity
        },
        counter: acc.counter + 1,
      }), { ...graph, counter: 0, length, text: 'Calculating similarities:' })
  })
  .share()

const result$ = r$
  .filter(({ counter, length }) => counter === length)
  .map(({ similarities }) => similarities)

result$.subscribe({
  next: v => setTimeout(() => console.log(JSON.stringify(v, null, 1)))
})

const progress$ = Rx.Observable.merge(params$, weights$, xValues$, r$)
  .map(({ text, counter, length }) => ({ text, progress: Math.floor(100 * counter / length) }))

progress$.subscribe({
  next: ({ text, progress }) => {
    log(`${text} progress ${progress}%`)
    if (progress >= 100) {
      console.log()
    }
  },
  error: err => console.error('something wrong occurred: ' + err)
})
