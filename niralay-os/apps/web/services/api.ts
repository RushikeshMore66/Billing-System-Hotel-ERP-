/**
 * NiralayOS API Client
 *
 * Typed fetch wrapper for the NiralayOS backend.
 * All endpoints follow the SuccessResponse<T> / PaginatedResponse<T> envelope.
 *
 * Auth tokens are stored in localStorage:
 *   niralay_access_token  — short-lived JWT
 *   niralay_refresh_token — long-lived refresh token
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ─── Token helpers ────────────────────────────────────────────────────────────

export const tokenStorage = {
  getAccess: (): string | null =>
    typeof window !== "undefined" ? localStorage.getItem("niralay_access_token") : null,
  getRefresh: (): string | null =>
    typeof window !== "undefined" ? localStorage.getItem("niralay_refresh_token") : null,
  set: (access: string, refresh: string): void => {
    localStorage.setItem("niralay_access_token", access);
    localStorage.setItem("niralay_refresh_token", refresh);
  },
  clear: (): void => {
    localStorage.removeItem("niralay_access_token");
    localStorage.removeItem("niralay_refresh_token");
    localStorage.removeItem("niralay_user");
  },
  setUser: (user: CurrentUser): void => {
    localStorage.setItem("niralay_user", JSON.stringify(user));
  },
  getUser: (): CurrentUser | null => {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem("niralay_user");
    return raw ? (JSON.parse(raw) as CurrentUser) : null;
  },
};

// ─── Response envelope types ──────────────────────────────────────────────────

export interface SuccessResponse<T> {
  success: true;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// ─── Domain types ─────────────────────────────────────────────────────────────

export interface CurrentUser {
  id: number;
  uuid: string;
  username: string;
  email: string;
  full_name: string;
  avatar?: string;
  department?: string;
  designation?: string;
  status: string;
  is_superuser: boolean;
  roles: string[];
  permissions: string[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Guest {
  id: number;
  uuid: string;
  full_name: string;
  email?: string;
  phone?: string;
  id_number?: string;
  nationality?: string;
  address?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
}

export interface Reservation {
  id: number;
  uuid: string;
  reservation_number: string;
  guest_id: number;
  room_id?: number;
  room_type_id: number;
  check_in_date: string;
  check_out_date: string;
  nights: number;
  adults: number;
  children: number;
  status: string;
  source: string;
  base_amount: number;
  tax_amount: number;
  total_amount: number;
  advance_paid: number;
  guest?: Guest;
  is_active: boolean;
  created_at: string;
}

export interface PropertyProfile {
  id: number;
  uuid: string;
  hotel_name: string;
  logo_url?: string;
  address_line1?: string;
  city?: string;
  state?: string;
  country?: string;
  email?: string;
  phone?: string;
  gst_number?: string;
  pan_number?: string;
  currency_code: string;
  timezone: string;
  language: string;
  check_in_time?: string;
  check_out_time?: string;
  invoice_prefix: string;
  star_rating?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Floor {
  id: number;
  uuid: string;
  floor_number: number;
  floor_name: string;
  display_order: number;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Amenity {
  id: number;
  uuid: string;
  name: string;
  icon?: string;
  description?: string;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
}

export interface BedType {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
}

export interface RoomType {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  base_price: string;
  weekend_price?: string;
  max_occupancy: number;
  extra_bed_allowed: boolean;
  extra_bed_charge?: string;
  status: string;
  amenities: Amenity[];
  images: RoomTypeImage[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoomTypeImage {
  id: number;
  image_url: string;
  caption?: string;
  display_order: number;
}

export interface Room {
  id: number;
  uuid: string;
  room_number: string;
  floor_id?: number;
  room_type_id: number;
  room_type?: { id: number; uuid: string; name: string; base_price: string };
  capacity: number;
  view?: string;
  status: string;
  housekeeping_status: string;
  maintenance_status: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Tax {
  id: number;
  uuid: string;
  name: string;
  code: string;
  tax_type: string;
  rate: string;
  is_inclusive: boolean;
  applies_to: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaymentMethod {
  id: number;
  uuid: string;
  name: string;
  code: string;
  payment_type: string;
  is_system: boolean;
  requires_reference: boolean;
  icon?: string;
  is_active: boolean;
  created_at: string;
}

export interface Currency {
  id: number;
  uuid: string;
  code: string;
  name: string;
  symbol: string;
  exchange_rate: string;
  decimal_places: number;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface Season {
  id: number;
  uuid: string;
  name: string;
  start_date: string;
  end_date: string;
  priority: number;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface RatePlan {
  id: number;
  uuid: string;
  name: string;
  code: string;
  description?: string;
  meal_plan: string;
  is_default: boolean;
  min_stay_nights: number;
  max_stay_nights?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuItem {
  id: number;
  uuid: string;
  item_code: string;
  name: string;
  description?: string;
  menu_category_id?: number;
  kitchen_station_id?: number;
  tax_id?: number;
  price: string;
  cost_price?: string;
  food_type: string;
  is_available: boolean;
  prep_time_minutes?: number;
  image_url?: string;
  allergens?: string;
  calories?: number;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RestaurantTable {
  id: number;
  uuid: string;
  table_number: string;
  capacity: number;
  section?: string;
  location_type: string;
  status: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: number;
  uuid: string;
  name: string;
  code: string;
  description?: string;
  is_system: boolean;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Designation {
  id: number;
  uuid: string;
  name: string;
  code: string;
  department_id?: number;
  description?: string;
  is_system: boolean;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessSettings {
  id: number;
  uuid: string;
  invoice_number_format: string;
  reservation_number_format: string;
  invoice_sequence_start: number;
  reservation_sequence_start: number;
  timezone: string;
  date_format: string;
  time_format: string;
  currency_format: string;
  decimal_precision: number;
  language: string;
  auto_backup_enabled: boolean;
  auto_backup_frequency: string;
  backup_retention_days: number;
  allow_partial_payment: boolean;
  tax_inclusive_by_default: boolean;
  minimum_advance_payment_pct: number;
  updated_at: string;
}

// ─── HTTP client ──────────────────────────────────────────────────────────────

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function getAuthHeaders(token?: string | null): HeadersInit {
  const accessToken = token ?? tokenStorage.getAccess();
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  isRetry = false
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers ?? {}),
    },
  });

  if (res.status === 401 && !isRetry) {
    if (path.includes("/auth/refresh") || path.includes("/auth/login")) {
      // Extract real error message from API response body
      let detail = "Authentication failed";
      try {
        const body = await res.json();
        detail = body?.detail ?? body?.message ?? detail;
      } catch {
        // ignore
      }
      throw new Error(detail);
    }

    if (isRefreshing) {
      return new Promise<T>((resolve) => {
        addRefreshSubscriber((newToken) => {
          resolve(apiFetch<T>(path, options, true));
        });
      });
    }

    isRefreshing = true;
    const refreshToken = tokenStorage.getRefresh();

    if (!refreshToken) {
      isRefreshing = false;
      tokenStorage.clear();
      if (typeof window !== "undefined") window.location.href = "/login";
      throw new Error("Session expired");
    }

    try {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!refreshRes.ok) throw new Error("Refresh failed");

      const body = await refreshRes.json();
      const tokens = body.data as TokenResponse;
      
      tokenStorage.set(tokens.access_token, tokens.refresh_token);
      isRefreshing = false;
      onRefreshed(tokens.access_token);
      
      return apiFetch<T>(path, options, true);
    } catch (err) {
      isRefreshing = false;
      tokenStorage.clear();
      if (typeof window !== "undefined") window.location.href = "/login";
      throw new Error("Session expired");
    }
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? body?.message ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(`API error ${res.status}: ${detail}`);
  }

  return res.json() as Promise<T>;
}

// ─── Property API ─────────────────────────────────────────────────────────────

export const propertyApi = {
  getProfile: () =>
    apiFetch<SuccessResponse<PropertyProfile>>("/property/profile"),

  updateProfile: (data: Partial<PropertyProfile>) =>
    apiFetch<SuccessResponse<PropertyProfile>>("/property/profile", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  listFloors: (params?: { search?: string; status?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<Floor>>(
      `/property/floors?${new URLSearchParams(params as Record<string, string> ?? {})}`
    ),

  listAmenities: (params?: { search?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<Amenity>>(
      `/property/amenities?${new URLSearchParams(params as Record<string, string> ?? {})}`
    ),

  listRoomTypes: (params?: { search?: string; status?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<RoomType>>(
      `/property/room-types?${new URLSearchParams(params as Record<string, string> ?? {})}`
    ),

  listRooms: (params?: {
    search?: string;
    floor_id?: number;
    room_type_id?: number;
    status?: string;
    housekeeping_status?: string;
    maintenance_status?: string;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<Room>>(
      `/property/rooms?${new URLSearchParams(
        Object.fromEntries(
          Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
        )
      )}`
    ),

  getRoomStatusSummary: () =>
    apiFetch<SuccessResponse<Record<string, number>>>("/property/rooms/status-summary"),

  listTaxes: (params?: { applies_to?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<Tax>>(
      `/property/taxes?${new URLSearchParams(params as Record<string, string> ?? {})}`
    ),

  listPaymentMethods: () =>
    apiFetch<PaginatedResponse<PaymentMethod>>("/property/payment-methods"),

  listCurrencies: () =>
    apiFetch<PaginatedResponse<Currency>>("/property/currencies"),

  listSeasons: () =>
    apiFetch<PaginatedResponse<Season>>("/property/seasons"),

  listRatePlans: () =>
    apiFetch<PaginatedResponse<RatePlan>>("/property/rate-plans"),
};

// ─── Restaurant API ───────────────────────────────────────────────────────────

export const restaurantApi = {
  listMenuItems: (params?: {
    search?: string;
    menu_category_id?: number;
    food_type?: string;
    is_available?: boolean;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<MenuItem>>(
      `/restaurant/menu-items?${new URLSearchParams(
        Object.fromEntries(
          Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
        )
      )}`
    ),

  listTables: (params?: {
    search?: string;
    section?: string;
    status?: string;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<RestaurantTable>>(
      `/restaurant/tables?${new URLSearchParams(
        Object.fromEntries(
          Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
        )
      )}`
    ),

  getTableStatusSummary: () =>
    apiFetch<SuccessResponse<Record<string, number>>>("/restaurant/tables/status-summary"),
};

// ─── Organisation API ─────────────────────────────────────────────────────────

export const organizationApi = {
  listDepartments: () =>
    apiFetch<PaginatedResponse<Department>>("/organization/departments"),

  listDesignations: (department_id?: number) =>
    apiFetch<PaginatedResponse<Designation>>(
      `/organization/designations${department_id ? `?department_id=${department_id}` : ""}`
    ),
};

// ─── Business Settings API ───────────────────────────────────────────────────

export const settingsApi = {
  get: () =>
    apiFetch<SuccessResponse<BusinessSettings>>("/settings/business"),

  update: (data: Partial<BusinessSettings>) =>
    apiFetch<SuccessResponse<BusinessSettings>>("/settings/business", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

// ─── Auth API ─────────────────────────────────────────────────────────────────

export const authApi = {
  login: (data: any) =>
    apiFetch<SuccessResponse<TokenResponse>>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  logout: () =>
    apiFetch<SuccessResponse<any>>("/auth/logout", { method: "POST" }),
  me: () =>
    apiFetch<SuccessResponse<CurrentUser>>("/auth/me"),
};

// ─── Dashboard API ────────────────────────────────────────────────────────────

export const dashboardApi = {
  getWidgets: () =>
    apiFetch<SuccessResponse<any>>("/dashboard/widgets"),
};

// ─── Reservations API ─────────────────────────────────────────────────────────

export const guestApi = {
  list: (params?: { search?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<Guest>>(
      `/guests?${new URLSearchParams(
        Object.fromEntries(
          Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
        )
      )}`
    ),
  create: (data: Partial<Guest>) =>
    apiFetch<SuccessResponse<Guest>>("/guests", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export const reservationApi = {
  list: (params?: { search?: string; status?: string; page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<Reservation>>(
      `/reservations?${new URLSearchParams(
        Object.fromEntries(
          Object.entries(params ?? {}).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
        )
      )}`
    ),
  create: (data: Partial<Reservation>) =>
    apiFetch<SuccessResponse<Reservation>>("/reservations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<Reservation>) =>
    apiFetch<SuccessResponse<Reservation>>(`/reservations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};
