export function getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift()?.replace(/['"]+/g, '');
    console.log(`Read cookie ${name}:`, cookieValue);
    return cookieValue || null;
  }
  console.log(`Cookie ${name} not found`);
  return null;
}