export function valid(slot: number): boolean {
  return slot > 0
}

export async function alive(): Promise<boolean> {
  return true
}

export function numeric(x: unknown): x is number {
  return typeof x === 'number'
}

export const ready = (): boolean => true

export const checked = function (): boolean {
  return true
}

export const slotChecks = { ready: (): boolean => true }

export const slotMethods = {
  ready(): boolean {
    return true
  },
}

export class Gate {
  open(): boolean {
    return true
  }
}

export class Latch {
  _closed(): boolean {
    return false
  }
}

export class Door {
  ready = (): boolean => true
}

export class Port implements Eq<Port> {
  equals(other: Port): boolean {
    return this === other
  }
  checks() {
    return { ready(): boolean { return true } }
  }
}
