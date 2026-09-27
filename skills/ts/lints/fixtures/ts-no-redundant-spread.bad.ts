export {}
const a = [1, 2, 3]
const f = (n: number) => n > 1
const g = (n: number) => n * 2
const kept = [...a.filter(f)]
const doubled = [...a.map(g)]
