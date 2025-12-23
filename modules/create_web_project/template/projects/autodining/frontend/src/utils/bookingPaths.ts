export type BookingQueryParams = {
  people?: number | string | null;
  date?: string | null;
};

export function buildBookingHref(
  restaurantId: string,
  timeValue: string,
  params: BookingQueryParams = {}
): string {
  const encodedTime = encodeURIComponent(timeValue);
  const query = new URLSearchParams();

  if (params.people !== undefined && params.people !== null && params.people !== "") {
    query.set("people", String(params.people));
  }
  if (params.date) {
    query.set("date", params.date);
  }

  const queryString = query.toString();
  return queryString ? `/booking/${restaurantId}/${encodedTime}?${queryString}` : `/booking/${restaurantId}/${encodedTime}`;
}
