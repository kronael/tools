export {}
const a = [1, 2, 3]
const f = (n: number) => n > 1
const kept = a.filter(f)
const merged = [...a.filter(f), 99]
