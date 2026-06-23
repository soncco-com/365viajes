import test from 'node:test'
import assert from 'node:assert/strict'

import {
  formatDateOnly,
  formatDateTimeInLima,
  formatLongDateInLima,
  formatTimeInLima,
  todayInLima,
} from './date.js'

test('formatDateOnly preserves calendar dates without timezone conversion', () => {
  assert.equal(formatDateOnly('2026-06-21'), '21/06/2026')
  assert.equal(formatDateOnly('2024-02-29'), '29/02/2024')
})

test('formatDateOnly rejects null and invalid dates', () => {
  assert.equal(formatDateOnly(null, '-'), '-')
  assert.equal(formatDateOnly('2026-02-29', '-'), '-')
  assert.equal(formatDateOnly('2026-06-21T00:00:00Z', '-'), '-')
})

test('todayInLima uses the Lima calendar day before UTC midnight', () => {
  assert.equal(todayInLima(new Date('2026-06-22T03:30:00Z')), '2026-06-21')
})

test('todayInLima changes day at midnight in Lima', () => {
  assert.equal(todayInLima(new Date('2026-06-22T04:59:59Z')), '2026-06-21')
  assert.equal(todayInLima(new Date('2026-06-22T05:00:00Z')), '2026-06-22')
})

test('long dates use the Lima calendar day', () => {
  const formatted = formatLongDateInLima(new Date('2026-06-22T03:30:00Z'))
  assert.match(formatted, /21/)
  assert.doesNotMatch(formatted, /22/)
})

test('timestamps are formatted explicitly in Lima', () => {
  const timestamp = '2026-06-22T02:15:30Z'
  assert.equal(formatDateTimeInLima(timestamp), '21/06/2026, 21:15:30')
  assert.equal(formatDateTimeInLima(timestamp, { dateOnly: true }), '21/06/2026')
  assert.equal(formatTimeInLima(timestamp), '21:15:30')
})

test('timestamps without timezone information are rejected', () => {
  assert.equal(formatDateTimeInLima('2026-06-21T21:15:30', { fallback: '-' }), '-')
  assert.equal(formatTimeInLima('invalid', { fallback: '-' }), '-')
})
