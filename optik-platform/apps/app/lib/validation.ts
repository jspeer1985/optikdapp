export function required(value: unknown, message = 'This field is required') {
  if (value === undefined || value === null || value === '') throw new Error(message);
}

export function minLength(value: string, min: number, message?: string) {
  if ((value ?? '').length < min) throw new Error(message || `Must be at least ${min} characters`);
}

export function isAddress(value: string, message = 'Invalid address') {
  if (!/^\w{20,64}$/.test(value)) throw new Error(message);
}
