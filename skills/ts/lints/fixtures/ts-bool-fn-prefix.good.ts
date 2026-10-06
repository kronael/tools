interface Eq<T> {
  equals(other: T): boolean
}

export class Slot implements Eq<Slot> {
  constructor(readonly n: number) {}
  equals(other: Slot): boolean {
    return this.n === other.n
  }
  isValid(): boolean {
    return this.n > 0
  }
}

export const hasSlots = (slots: Slot[]): boolean => slots.length > 0

export function count(slots: Slot[]): number {
  return slots.length
}
