export const BUSINESS_TIME_ZONE = 'America/Lima'

const DATE_ONLY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/
const ISO_INSTANT_PATTERN = /^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/i

const zonedDateTimeFormatter = new Intl.DateTimeFormat('en-US', {
  timeZone: BUSINESS_TIME_ZONE,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
})

const longDateFormatter = new Intl.DateTimeFormat('es-PE', {
  timeZone: BUSINESS_TIME_ZONE,
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
})

const isLeapYear = (year) => year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)

const isValidDateOnly = (year, month, day) => {
  if (month < 1 || month > 12 || day < 1) return false

  const daysByMonth = [31, isLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  return day <= daysByMonth[month - 1]
}

const getZonedParts = (date) => {
  const parts = {}
  for (const part of zonedDateTimeFormatter.formatToParts(date)) {
    if (part.type !== 'literal') parts[part.type] = part.value
  }
  return parts
}

const parseInstant = (value) => {
  if (typeof value !== 'string' || !ISO_INSTANT_PATTERN.test(value)) return null

  const timestamp = Date.parse(value)
  return Number.isNaN(timestamp) ? null : new Date(timestamp)
}

export const todayInLima = (now = new Date()) => {
  if (!(now instanceof Date) || Number.isNaN(now.getTime())) return ''

  const { year, month, day } = getZonedParts(now)
  return `${year}-${month}-${day}`
}

export const formatDateOnly = (value, fallback = '') => {
  if (typeof value !== 'string') return fallback

  const match = DATE_ONLY_PATTERN.exec(value)
  if (!match) return fallback

  const [, year, month, day] = match
  if (!isValidDateOnly(Number(year), Number(month), Number(day))) return fallback

  return `${day}/${month}/${year}`
}

export const formatLongDateInLima = (now = new Date(), fallback = '') => {
  if (!(now instanceof Date) || Number.isNaN(now.getTime())) return fallback
  return longDateFormatter.format(now)
}

export const formatDateTimeInLima = (
  value,
  { dateOnly = false, includeSeconds = true, fallback = '' } = {},
) => {
  const date = parseInstant(value)
  if (!date) return fallback

  const { year, month, day, hour, minute, second } = getZonedParts(date)
  const formattedDate = `${day}/${month}/${year}`
  if (dateOnly) return formattedDate

  const formattedTime = includeSeconds ? `${hour}:${minute}:${second}` : `${hour}:${minute}`
  return `${formattedDate}, ${formattedTime}`
}

export const formatTimeInLima = (
  value,
  { includeSeconds = true, fallback = '' } = {},
) => {
  const date = parseInstant(value)
  if (!date) return fallback

  const { hour, minute, second } = getZonedParts(date)
  return includeSeconds ? `${hour}:${minute}:${second}` : `${hour}:${minute}`
}
