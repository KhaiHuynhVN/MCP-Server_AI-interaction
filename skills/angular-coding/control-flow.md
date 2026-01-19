# Control Flow (v17+)

## @if / @else if / @else

```html
@if (user) {
  <div>Welcome, {{ user.name }}</div>
} @else if (isLoading) {
  <div>Loading...</div>
} @else {
  <div>Please log in</div>
}
```

### With Variable Aliasing

```html
@if (user.profile.settings.theme; as theme) {
  <div>Current theme: {{ theme }}</div>
}
```

### Replace *ngIf

```html
<!-- Before -->
<div *ngIf="user; else loading">{{ user.name }}</div>
<ng-template #loading>Loading...</ng-template>

<!-- After -->
@if (user) {
  <div>{{ user.name }}</div>
} @else {
  <div>Loading...</div>
}
```

## @for

```html
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
}
```

### Track Expression (Required)

```html
<!-- By unique ID -->
@for (item of items; track item.id) { }

<!-- By index (static lists only) -->
@for (item of items; track $index) { }

<!-- By identity (avoid if possible) -->
@for (item of items; track item) { }
```

### Context Variables

```html
@for (item of items; track item.id; let idx = $index, first = $first, last = $last) {
  <div [class.first]="first" [class.last]="last">
    {{ idx }}: {{ item.name }}
  </div>
}
```

| Variable | Meaning |
|----------|---------|
| `$index` | Current index |
| `$first` | Is first item |
| `$last` | Is last item |
| `$even` | Is even index |
| `$odd` | Is odd index |
| `$count` | Total items |

### @empty Block

```html
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <div>No items found</div>
}
```

### Replace *ngFor

```html
<!-- Before -->
<div *ngFor="let item of items; trackBy: trackById; let i = index">
  {{ i }}: {{ item.name }}
</div>

<!-- After -->
@for (item of items; track item.id; let i = $index) {
  <div>{{ i }}: {{ item.name }}</div>
}
```

## @switch

```html
@switch (status) {
  @case ('active') {
    <span class="badge-active">Active</span>
  }
  @case ('pending') {
    <span class="badge-pending">Pending</span>
  }
  @case ('inactive') {
    <span class="badge-inactive">Inactive</span>
  }
  @default {
    <span class="badge-unknown">Unknown</span>
  }
}
```

### Multiple Cases

```html
@switch (role) {
  @case ('admin')
  @case ('superadmin') {
    <admin-panel />
  }
  @case ('user') {
    <user-panel />
  }
}
```

### Replace [ngSwitch]

```html
<!-- Before -->
<div [ngSwitch]="status">
  <span *ngSwitchCase="'active'">Active</span>
  <span *ngSwitchCase="'pending'">Pending</span>
  <span *ngSwitchDefault>Unknown</span>
</div>

<!-- After -->
@switch (status) {
  @case ('active') { <span>Active</span> }
  @case ('pending') { <span>Pending</span> }
  @default { <span>Unknown</span> }
}
```

## @defer (Lazy Loading)

```html
@defer {
  <heavy-component />
}
```

### With Loading/Error States

```html
@defer {
  <heavy-component />
} @loading {
  <div>Loading component...</div>
} @error {
  <div>Failed to load</div>
} @placeholder {
  <div>Placeholder content</div>
}
```

### Trigger Conditions

```html
<!-- On viewport (lazy load when visible) -->
@defer (on viewport) {
  <heavy-component />
}

<!-- On interaction -->
@defer (on interaction) {
  <heavy-component />
} @placeholder {
  <button>Load more</button>
}

<!-- On timer -->
@defer (on timer(2000ms)) {
  <heavy-component />
}

<!-- On idle -->
@defer (on idle) {
  <heavy-component />
}

<!-- When condition -->
@defer (when isReady) {
  <heavy-component />
}

<!-- Prefetch -->
@defer (on viewport; prefetch on idle) {
  <heavy-component />
}
```

### Minimum Display Times

```html
@defer {
  <heavy-component />
} @loading (minimum 500ms) {
  <spinner />
} @placeholder (minimum 200ms) {
  <skeleton />
}
```

## Migration

Use Angular CLI schematic:

```bash
ng generate @angular/core:control-flow
```

## Best Practices

1. **Always use `track`** in @for - required and improves performance
2. **Use unique IDs for track** - avoid $index for dynamic lists
3. **Prefer @if over *ngIf** - cleaner syntax, better performance
4. **Use @defer for heavy components** - improves initial load
5. **Add @placeholder and @loading** - better UX during lazy load
