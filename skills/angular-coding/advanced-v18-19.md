# Advanced Features (v18-19+)

## Signal Inputs (v18+)

### Basic Input

```typescript
@Component({
  selector: 'bls-user-card',
  template: `<div>{{ $name() }}</div>`,
})
export class UserCardComponent {
  // Signal input
  $name = input<string>('');
  
  // Required input
  $id = input.required<string>();
  
  // With alias
  $userName = input<string>('', { alias: 'name' });
}
```

### Usage in Template

```html
<bls-user-card [name]="userName" [id]="userId" />
```

### Transform Input

```typescript
$disabled = input(false, {
  transform: booleanAttribute
});

$count = input(0, {
  transform: numberAttribute
});
```

## Signal Outputs (v18+)

### Basic Output

```typescript
@Component({
  selector: 'bls-button',
})
export class ButtonComponent {
  // Signal output
  clicked = output<void>();
  
  // With payload
  selected = output<Item>();
  
  onClick() {
    this.clicked.emit();
  }
  
  onSelect(item: Item) {
    this.selected.emit(item);
  }
}
```

### Usage in Template

```html
<bls-button (clicked)="handleClick()" (selected)="handleSelect($event)" />
```

## Model Inputs (v18+)

Two-way binding with signals:

```typescript
@Component({
  selector: 'bls-counter',
  template: `
    <button (click)="decrement()">-</button>
    <span>{{ $value() }}</span>
    <button (click)="increment()">+</button>
  `,
})
export class CounterComponent {
  // Model input enables two-way binding
  $value = model(0);
  
  increment() {
    this.$value.update(v => v + 1);
  }
  
  decrement() {
    this.$value.update(v => v - 1);
  }
}
```

### Usage with Banana-in-a-box

```html
<!-- Two-way binding with signal -->
<bls-counter [($value)]="$count" />

<!-- Or with regular property -->
<bls-counter [($value)]="count" />
```

## linkedSignal (v19+)

Dependent state that resets when source changes:

```typescript
$items = signal<Item[]>([]);
$selectedIndex = linkedSignal(() => this.$items().length > 0 ? 0 : -1);

// selectedIndex auto-resets when items change
```

### With Write Function

```typescript
$items = signal<Item[]>([]);

$selectedId = linkedSignal({
  source: this.$items,
  computation: (items) => items[0]?.id ?? null,
});

// Can still manually update
selectItem(id: string) {
  this.$selectedId.set(id);
}
```

## Resource API (v19+)

Async data loading with signals:

```typescript
$userId = signal<string>('123');

$userResource = resource({
  request: () => this.$userId(),
  loader: async ({ request: userId }) => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  },
});

// Access in template
template: `
  @if ($userResource.isLoading()) {
    <spinner />
  } @else if ($userResource.error()) {
    <error-message />
  } @else {
    <user-profile [user]="$userResource.value()" />
  }
`
```

### Resource with RxJS

```typescript
$userResource = rxResource({
  request: () => this.$userId(),
  loader: ({ request: userId }) => this._http.get<User>(`/api/users/${userId}`),
});
```

### Reload Resource

```typescript
reload() {
  this.$userResource.reload();
}
```

## Zoneless (v18+ Experimental)

### Enable Zoneless

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideExperimentalZonelessChangeDetection(),
    // other providers
  ],
};
```

### Considerations

- Must use OnPush change detection
- Must use signals or manual `markForCheck()`
- Better performance, smaller bundle size
- Some third-party libraries may not work

## afterRender / afterNextRender (v17+)

```typescript
constructor() {
  afterRender(() => {
    // Runs after every render
    console.log('Component rendered');
  });
  
  afterNextRender(() => {
    // Runs once after next render
    this.initializeChart();
  });
}
```

### With Phases

```typescript
afterRender({
  read: () => {
    // Read DOM measurements
    const height = this.element.offsetHeight;
  },
  write: () => {
    // Write to DOM
    this.element.style.width = '100px';
  },
});
```

## View Queries with Signals (v17+)

```typescript
// Signal-based view queries
$input = viewChild<ElementRef>('inputRef');
$items = viewChildren<ItemComponent>(ItemComponent);

// Content queries
$header = contentChild<TemplateRef<any>>('header');
$tabs = contentChildren<TabComponent>(TabComponent);
```

### Usage

```typescript
focusInput() {
  this.$input()?.nativeElement.focus();
}

getItemCount() {
  return this.$items().length;
}
```

## Best Practices v18-19

1. **Prefer signal inputs over @Input()** - better type inference
2. **Use model() for two-way binding** - cleaner than input + output
3. **Use linkedSignal for dependent state** - auto-reset on source change
4. **Use resource for async data** - built-in loading/error states
5. **Consider zoneless** - better performance for new projects
6. **Use afterRender for DOM operations** - safer than ngAfterViewInit
