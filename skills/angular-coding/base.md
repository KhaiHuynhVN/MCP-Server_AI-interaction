# Base Patterns (All Versions)

## Component Structure

```typescript
@Component({
  selector: 'bls-feature-name',
  templateUrl: './feature-name.component.html',
  styleUrls: ['./feature-name.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeatureNameComponent implements OnInit, OnDestroy {
  // 1. ViewChild/ViewChildren
  @ViewChild(MatSort) sort: MatSort;

  // 2. Public properties
  $state = signal<ComponentState>('idle');  // Signal: prefix $
  isLoading$ = new BehaviorSubject<boolean>(false);  // Observable: suffix $
  dataSource = new MatTableDataSource<Model>([]);

  // 3. Private properties
  private _destroyed$ = new Subject<void>();
  private _fetch$ = new Subject<void>();

  // 4. Injected services (use inject() function - v14+)
  private _api = inject(ApiService);
  private _cdr = inject(ChangeDetectorRef);

  // -----------------------------------------------------------------------------------------------------
  // @ Hooks
  // -----------------------------------------------------------------------------------------------------
  ngOnInit(): void {}

  ngOnDestroy(): void {
    this._destroyed$.next();
    this._destroyed$.complete();
  }

  // -----------------------------------------------------------------------------------------------------
  // @ Public Methods
  // -----------------------------------------------------------------------------------------------------
  publicMethod() {}

  // -----------------------------------------------------------------------------------------------------
  // @ Private Methods
  // -----------------------------------------------------------------------------------------------------
  private _privateMethod() {}
}
```

## Dependency Injection

### v14+ (Preferred)

```typescript
private _api = inject(ApiService);
private _cdr = inject(ChangeDetectorRef);
```

### v13 (Constructor)

```typescript
constructor(
  private _api: ApiService,
  private _cdr: ChangeDetectorRef
) {}
```

## RxJS Patterns

### Subscription Cleanup

```typescript
this._fetch$
  .pipe(takeUntil(this._destroyed$))
  .subscribe();
```

### Data Loading

```typescript
private _load() {
  this._fetch$
    .pipe(
      takeUntil(this._destroyed$),
      startWith('init'),
      debounceTime(100),
      tap(() => this.isLoading$.next(true)),
      switchMap(() => this._api.list()),
      tap((res) => {
        this.dataSource.data = res?.data ?? [];
        this.isLoading$.next(false);
      }),
      catchError((error) => {
        console.error(error);
        this.isLoading$.next(false);
        this._toast.error('Something went wrong');
        return of();
      })
    )
    .subscribe();
}
```

### Search with Debounce

```typescript
this.searchControl.valueChanges
  .pipe(debounceTime(300))
  .subscribe(() => {
    this.page.index = 0;
    this._fetch$.next();
  });
```

## Service Structure

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureService extends BaseApiService {
  override _baseUrl = `${environment.apiUrl}/feature`;

  list(options: ListOptions) {
    return this._http
      .get<ResponseModel>(`${this._baseUrl}/search`, { params })
      .pipe(
        BaseAPIOperator.responseHandler(),
        map((res) => this._transform(res))
      );
  }

  // -----------------------------------------------------------------------------------------------------
  // @ Private Methods
  // -----------------------------------------------------------------------------------------------------
  private _transform(res: any): Model {}
}
```

## Error Handling

```typescript
catchError((error) => {
  console.error(error);
  this._loader.hide();
  this._toast.error('Oops, something went wrong. Please try again later.');
  return of(null);
})
```

## Section Separators

```typescript
// -----------------------------------------------------------------------------------------------------
// @ Accessors
// -----------------------------------------------------------------------------------------------------

// -----------------------------------------------------------------------------------------------------
// @ Hooks
// -----------------------------------------------------------------------------------------------------

// -----------------------------------------------------------------------------------------------------
// @ Public Methods
// -----------------------------------------------------------------------------------------------------

// -----------------------------------------------------------------------------------------------------
// @ Private Methods
// -----------------------------------------------------------------------------------------------------
```

## Form Patterns

### Reactive Form Setup

```typescript
// Component
private _fb = inject(FormBuilder);

form = this._fb.group({
  name: ['', [Validators.required, Validators.minLength(3)]],
  email: ['', [Validators.required, Validators.email]],
  phone: ['', [Validators.pattern(/^\d{10}$/)]],
});

// Submit
onSubmit() {
  if (this.form.invalid) {
    this.form.markAllAsTouched();
    return;
  }
  const data = this.form.getRawValue();
  // API call...
}
```

### FormArray

```typescript
form = this._fb.group({
  items: this._fb.array<FormGroup>([]),
});

get itemsArray() {
  return this.form.get('items') as FormArray;
}

addItem() {
  this.itemsArray.push(this._fb.group({
    name: ['', Validators.required],
    quantity: [1, [Validators.required, Validators.min(1)]],
  }));
}

removeItem(index: number) {
  this.itemsArray.removeAt(index);
}
```

### Custom Validator

```typescript
// validators/custom.validators.ts
export class CustomValidators {
  static match(controlName: string, matchingName: string): ValidatorFn {
    return (group: AbstractControl): ValidationErrors | null => {
      const control = group.get(controlName);
      const matching = group.get(matchingName);
      
      if (control?.value !== matching?.value) {
        matching?.setErrors({ match: true });
        return { match: true };
      }
      return null;
    };
  }
}

// Usage
form = this._fb.group({
  password: ['', Validators.required],
  confirmPassword: ['', Validators.required],
}, { validators: CustomValidators.match('password', 'confirmPassword') });
```

### Error Display (Template)

```html
<!-- Single field -->
@if (form.get('email')?.touched && form.get('email')?.errors) {
  <mat-error>
    @if (form.get('email')?.hasError('required')) { Email là bắt buộc }
    @if (form.get('email')?.hasError('email')) { Email không hợp lệ }
  </mat-error>
}

<!-- Reusable approach - dùng Pipe hoặc Directive -->
<mat-error>{{ form.get('email') | formError }}</mat-error>
```

## Performance Patterns

### Object Mapping > Array Loop

**❌ Tránh - O(n) mỗi lần lookup:**

```typescript
getStatusLabel(code: string): string {
  return this.statuses.find(s => s.code === code)?.label ?? 'Unknown';
}
```

**✅ Ưu tiên - O(1) lookup:**

```typescript
private _statusMap: Record<string, string> = {
  active: 'Hoạt động',
  inactive: 'Ngừng hoạt động',
  pending: 'Chờ duyệt',
};

getStatusLabel = (code: string) => this._statusMap[code] ?? 'Unknown';
```

## Angular-Native Solutions

| Vấn đề | ❌ Tránh | ✅ Dùng Angular |
|--------|----------|-----------------|
| Validation | Tự viết if/else | `Validators.required`, `Validators.email` |
| Format data | getter trong component | `Pipe` trong template |
| DOM behavior | `document.getElementById` | `Directive` + `ElementRef` |
| Route protect | if check trong component | `Guard` |
| HTTP transform | logic trong service | `Interceptor` |
| Pre-fetch data | ngOnInit API call | `Resolver` |

## SOLID in Angular

| Principle | Application |
|-----------|-------------|
| **S**ingle Responsibility | 1 component = 1 việc. Logic → Service |
| **O**pen/Closed | `@Input()` để extend, không sửa gốc |
| **L**iskov Substitution | Derived class thay thế được base |
| **I**nterface Segregation | Interface nhỏ, không force unused methods |
| **D**ependency Inversion | `inject()` service, không `new` |

## DO NOT

- Forget `takeUntil(_destroyed$)` on subscriptions
- Use Default change detection (always OnPush)
- Over-comment obvious code
- Create unnecessary files
- Loop array để tìm item (dùng Map/Record)
- Tự viết validation khi Angular có Validators
- Tự format data khi có thể dùng Pipe
- Direct DOM manipulation (dùng Directive)
- Business logic trong Component (chuyển vào Service)
