interface Eq<T> {
  equals(other: T): boolean
}

export class Slot implements Eq<Slot> {
  constructor(readonly n: number) {}
  equals(other: Slot): boolean {
    return this.n === other.n
  }
}

export class Gauge {
  constructor(readonly n: number) {}
  isValid(): boolean {
    return this.n > 0
  }
  _isCached(): boolean {
    return false
  }
  #hasOwner(): boolean {
    return false
  }
  get open(): boolean {
    return this.n > 0
  }
}

export abstract class Seat implements Eq<Seat> {
  equals(other: Seat): boolean {
    return this === other
  }
}

export const Bench = class implements Eq<number> {
  equals(other: number): boolean {
    return other > 0
  }
}

export abstract class Rank {
  abstract equals(other: Rank): boolean
}

export class Tier extends Rank {
  override equals(other: Rank): boolean {
    return this === other
  }
  canMove = (): boolean => true
}

export const hasSlots = (slots: Slot[]): boolean => slots.length > 0

export const slotChecks = {
  isEmpty: (slots: Slot[]): boolean => !slots.length,
  'hasRoom': (slots: Slot[]): boolean => slots.length < 8,
}

export async function hasOwner(): Promise<boolean> {
  return true
}

export function isSlot(x: unknown): x is Slot {
  return x instanceof Slot
}

export function count(slots: Slot[]): number {
  return slots.length
}
