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

  listMenuCategories: () =>
    apiFetch<SuccessResponse<any[]>>("/restaurant/menu-categories"),
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
  getOverview: () =>
    apiFetch<SuccessResponse<DashboardOverview>>("/dashboard/overview"),
  getRevenueWidget: () =>
    apiFetch<SuccessResponse<any>>("/dashboard/revenue"),
  getOccupancyWidget: () =>
    apiFetch<SuccessResponse<any>>("/dashboard/occupancy"),
  getInventoryWidget: () =>
    apiFetch<SuccessResponse<any>>("/dashboard/inventory"),
  getFinanceWidget: () =>
    apiFetch<SuccessResponse<any>>("/dashboard/finance"),
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

// ─── Inventory API ────────────────────────────────────────────────────────────

export interface InventoryCategory {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  display_order: number;
  is_active: boolean;
}

export interface StoreLocation {
  id: number;
  uuid: string;
  name: string;
  code: string;
  description?: string;
  display_order: number;
}

export interface InventoryItem {
  id: number;
  uuid: string;
  sku: string;
  name: string;
  description?: string;
  category_id?: number;
  category?: { id: number; name: string; color?: string; icon?: string };
  location_id?: number;
  location?: { id: number; name: string; code: string };
  unit: string;
  item_type: string;
  current_stock: number;
  minimum_stock: number;
  reorder_level?: number;
  maximum_stock?: number;
  purchase_price?: number;
  supplier_name?: string;
  supplier_contact?: string;
  has_expiry: boolean;
  expiry_date?: string;
  batch_number?: string;
  tax_rate?: number;
  notes?: string;
  image_url?: string;
  stock_level: "ok" | "low" | "critical";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockMovement {
  id: number;
  item_id: number;
  movement_type: string;
  quantity: number;
  stock_before: number;
  stock_after: number;
  unit_cost?: number;
  total_cost?: number;
  reference_type?: string;
  reference_id?: string;
  supplier_name?: string;
  notes?: string;
  movement_date: string;
  recorded_by?: string;
  created_at: string;
}

function buildParams(params: Record<string, any>): string {
  return new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)])
    )
  ).toString();
}

export const inventoryApi = {
  // Categories
  listCategories: () =>
    apiFetch<SuccessResponse<InventoryCategory[]>>("/inventory/categories"),
  createCategory: (data: Partial<InventoryCategory>) =>
    apiFetch<SuccessResponse<InventoryCategory>>("/inventory/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateCategory: (id: number, data: Partial<InventoryCategory>) =>
    apiFetch<SuccessResponse<InventoryCategory>>(`/inventory/categories/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deleteCategory: (id: number) =>
    apiFetch<SuccessResponse<null>>(`/inventory/categories/${id}`, { method: "DELETE" }),

  // Locations
  listLocations: () =>
    apiFetch<SuccessResponse<StoreLocation[]>>("/inventory/locations"),
  createLocation: (data: Partial<StoreLocation>) =>
    apiFetch<SuccessResponse<StoreLocation>>("/inventory/locations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteLocation: (id: number) =>
    apiFetch<SuccessResponse<null>>(`/inventory/locations/${id}`, { method: "DELETE" }),

  // Items
  listItems: (params?: {
    search?: string;
    category_id?: number;
    location_id?: number;
    item_type?: string;
    stock_level?: string;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<InventoryItem>>(`/inventory/items?${buildParams(params ?? {})}`),
  createItem: (data: Partial<InventoryItem> & { current_stock?: number }) =>
    apiFetch<SuccessResponse<InventoryItem>>("/inventory/items", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getItem: (id: number) =>
    apiFetch<SuccessResponse<InventoryItem>>(`/inventory/items/${id}`),
  updateItem: (id: number, data: Partial<InventoryItem>) =>
    apiFetch<SuccessResponse<InventoryItem>>(`/inventory/items/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deleteItem: (id: number) =>
    apiFetch<SuccessResponse<null>>(`/inventory/items/${id}`, { method: "DELETE" }),
  getLowStockAlerts: (limit?: number) =>
    apiFetch<SuccessResponse<InventoryItem[]>>(`/inventory/items/alerts${limit ? `?limit=${limit}` : ""}`),

  // Movements
  recordMovement: (itemId: number, data: Partial<StockMovement> & { movement_type: string; quantity: number }) =>
    apiFetch<SuccessResponse<StockMovement>>(`/inventory/items/${itemId}/movements`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  listMovements: (itemId: number, params?: { page?: number; size?: number }) =>
    apiFetch<PaginatedResponse<StockMovement>>(
      `/inventory/items/${itemId}/movements?${buildParams(params ?? {})}`
    ),
};

// ─── Expenses API ─────────────────────────────────────────────────────────────

export interface ExpenseCategory {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  display_order: number;
  is_system: boolean;
  is_active: boolean;
}

export interface Expense {
  id: number;
  uuid: string;
  category_id?: number;
  category?: { id: number; name: string };
  description: string;
  amount: number;
  tax_amount: number;
  total_amount: number;
  expense_date: string;
  payment_method?: string;
  vendor_name?: string;
  vendor_contact?: string;
  reference_number?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
}

export const expenseApi = {
  listCategories: () =>
    apiFetch<SuccessResponse<ExpenseCategory[]>>("/expenses/categories"),
  createCategory: (data: { name: string; description?: string }) =>
    apiFetch<SuccessResponse<ExpenseCategory>>("/expenses/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  list: (params?: {
    search?: string;
    category_id?: number;
    payment_method?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<Expense>>(`/expenses?${buildParams(params ?? {})}`),
  create: (data: Partial<Expense>) =>
    apiFetch<SuccessResponse<Expense>>("/expenses", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<Expense>) =>
    apiFetch<SuccessResponse<Expense>>(`/expenses/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    apiFetch<SuccessResponse<null>>(`/expenses/${id}`, { method: "DELETE" }),
};

// ─── Billing API ──────────────────────────────────────────────────────────────

export interface BillItem {
  id: number;
  bill_id: number;
  item_type: string;
  description: string;
  menu_item_id?: number;
  quantity: number;
  unit_price: number;
  discount_pct: number;
  tax_rate: number;
  amount: number;
  tax_amount: number;
  total: number;
  notes?: string;
}

export interface PaymentRecord {
  id: number;
  uuid: string;
  bill_id: number;
  amount: number;
  payment_date: string;
  status: string;
  payment_type?: string;
  reference_number?: string;
  transaction_id?: string;
  notes?: string;
  received_by?: string;
}

export interface Bill {
  id: number;
  uuid: string;
  bill_number: string;
  bill_date: string;
  bill_type: string;
  reservation_id?: number;
  guest_id?: number;
  table_number?: string;
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  amount_due: number;
  status: string;
  notes?: string;
  gst_number?: string;
  void_reason?: string;
  items: BillItem[];
  payments: PaymentRecord[];
  created_at: string;
}

export const billingApi = {
  listBills: (params?: {
    search?: string;
    status?: string;
    bill_type?: string;
    reservation_id?: number;
    guest_id?: number;
    date_from?: string;
    date_to?: string;
    page?: number;
    size?: number;
  }) =>
    apiFetch<PaginatedResponse<Bill>>(`/billing/bills?${buildParams(params ?? {})}`),
  createBill: (data: {
    reservation_id?: number;
    guest_id?: number;
    table_number?: string;
    bill_type?: string;
    items?: Partial<BillItem>[];
    notes?: string;
    gst_number?: string;
  }) =>
    apiFetch<SuccessResponse<Bill>>("/billing/bills", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getBill: (id: number) =>
    apiFetch<SuccessResponse<Bill>>(`/billing/bills/${id}`),
  addItems: (id: number, items: Partial<BillItem>[]) =>
    apiFetch<SuccessResponse<Bill>>(`/billing/bills/${id}/items`, {
      method: "POST",
      body: JSON.stringify(items),
    }),
  issueBill: (id: number) =>
    apiFetch<SuccessResponse<Bill>>(`/billing/bills/${id}/issue`, { method: "POST" }),
  recordPayment: (id: number, data: { amount: number; payment_type?: string; reference_number?: string; notes?: string }) =>
    apiFetch<SuccessResponse<PaymentRecord>>(`/billing/bills/${id}/payments`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  voidBill: (id: number, reason: string) =>
    apiFetch<SuccessResponse<Bill>>(`/billing/bills/${id}/void?reason=${encodeURIComponent(reason)}`, {
      method: "POST",
    }),
};

// ─── Dashboard types ──────────────────────────────────────────────────────────

export interface DashboardKPI {
  today: number;
  yesterday: number;
  change_pct: number;
  hotel_revenue: number;
  restaurant_revenue: number;
  other_revenue: number;
}

export interface DashboardOccupancy {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  occupancy_pct: number;
  current_guests: number;
}

export interface DashboardReservation {
  id: number;
  reservation_number: string;
  guest_name: string;
  room_number?: string;
  room_type?: string;
  check_in: string;
  check_out: string;
  nights: number;
  amount: number;
  status: string;
  source: string;
  created_at: string;
}

export interface InventoryAlert {
  id: number;
  item_name: string;
  current_quantity: number;
  unit: string;
  minimum_quantity: number;
  level: "ok" | "low" | "critical";
  category?: string;
}

export interface ActivityItem {
  id: number;
  event_type: string;
  description: string;
  actor?: string;
  resource_id?: string;
  metadata: Record<string, any>;
  occurred_at: string;
}

export interface DashboardOverview {
  kpis: {
    revenue: DashboardKPI;
    occupancy: DashboardOccupancy;
    reservation: {
      today_total: number;
      today_checkins: number;
      today_checkouts: number;
      pending_arrivals: number;
    };
    restaurant: {
      active_orders: number;
      today_revenue: number;
      dine_in_orders: number;
      room_service_orders: number;
      takeaway_orders: number;
    };
    finance: {
      pending_payments: number;
      pending_count: number;
      monthly_revenue: number;
      net_profit_est: number;
    };
    inventory: {
      low_stock_count: number;
      critical_count: number;
      ok_count: number;
    };
    employee: {
      total_active: number;
      present_today: number;
      on_leave: number;
    };
    as_of: string;
  };
  today_reservations: DashboardReservation[];
  inventory_alerts: InventoryAlert[];
  recent_activities: ActivityItem[];
  charts: {
    revenue_trend: Array<{ day: string; date: string; revenue: number; last_week: number }>;
    occupancy_trend: Array<{ hour: string; hotel_pct: number; restaurant_pct: number }>;
    reservation_trend: Array<{ date: string; new_reservations: number; check_ins: number; check_outs: number }>;
    cash_flow_trend: Array<{ date: string; inflow: number; outflow: number; net: number }>;
    monthly_revenue: Array<{ month: string; year: number; total: number; hotel: number; restaurant: number }>;
  };
  as_of: string;
}
