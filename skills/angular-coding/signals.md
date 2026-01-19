# Signals (v16+)

## Overview

- **v16**: Developer Preview
- **v17+**: Stable

## Writable Signals

```typescript
// Create with initial value
$count = signal(0);
$user = signal<User | null>(null);
$items = signal<Item[]>([]);

// Read value
const count = this.$count();
const user = this.$user();

// Update value
this.$count.set(5);
this.$count.update(v => v + 1);
this.$user.set(newUser);
```

## Computed Signals

```typescript
$count = signal(0);
$doubleCount = computed(() => this.$count() * 2);

// With multiple dependencies
$firstName = signal('John');
$lastName = signal('Doe');
$fullName = computed(() => `${this.$firstName()} ${this.$lastName()}`);
```

## Effect

```typescript
constructor() {
  // Runs when any read signal changes
  effect(() => {
    console.log('Count changed:', this.$count());
  });
}
```

**Important:** Effect runs in injection context. Use in constructor or with `runInInjectionContext`.

## Signal in Service

```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  // Private writable signal
  private _$user = signal<User | null>(null);
  
  // Public readonly signal
  readonly $user = this._$user.asReadonly();
  
  // Computed from signal
  readonly $isLoggedIn = computed(() => this._$user() !== null);
  
  setUser(user: User) {
    this._$user.set(user);
  }
  
  clearUser() {
    this._$user.set(null);
  }
}
```

## Signal in Component

```typescript
@Component({
  standalone: true,
  template: `
    <div>Count: {{ $count() }}</div>
    <div>Double: {{ $doubleCount() }}</div>
    <button (click)="increment()">+</button>
  `,
})
export class CounterComponent {
  $count = signal(0);
  $doubleCount = computed(() => this.$count() * 2);
  
  increment() {
    this.$count.update(v => v + 1);
  }
}
```

## RxJS Interop

### toSignal

```typescript
import { toSignal } from '@angular/core/rxjs-interop';

// Convert Observable to Signal
$data = toSignal(this._api.getData());

// With initial value
$data = toSignal(this._api.getData(), { initialValue: [] });

// With requireSync for sync observables
$route = toSignal(this._route.params, { requireSync: true });
```

### toObservable

```typescript
import { toObservable } from '@angular/core/rxjs-interop';

$count = signal(0);

// Convert Signal to Observable
count$ = toObservable(this.$count);

// Use in RxJS pipe
count$.pipe(
  debounceTime(300),
  switchMap(count => this._api.search(count))
).subscribe();
```

## Naming Convention

```typescript
// Signal: prefix $
$user = signal<User | null>(null);
$count = signal(0);
$items = signal<Item[]>([]);

// Observable: suffix $
isLoading$ = new BehaviorSubject<boolean>(false);
data$ = this._api.getData();
```

## When to Use Signals vs Observables

### Use Signals For:
- Synchronous state
- UI state (loading, error, selected)
- Derived/computed values
- Simple state management

### Use Observables For:
- Async operations (HTTP, WebSocket)
- Complex event streams
- Multiple subscribers with different needs
- Time-based operations (debounce, throttle)

## Migration Tips

```typescript
// Before: BehaviorSubject
isLoading$ = new BehaviorSubject<boolean>(false);
this.isLoading$.next(true);
const loading = this.isLoading$.value;

// After: Signal
$isLoading = signal(false);
this.$isLoading.set(true);
const loading = this.$isLoading();
```

## Best Practices

1. **Prefix signals with `$`** for easy identification
2. **Use computed for derived state** - auto-updates when dependencies change
3. **Use `asReadonly()`** to expose read-only signals from services
4. **Avoid effects for state changes** - use computed instead when possible
5. **Use toSignal/toObservable** for RxJS integration
