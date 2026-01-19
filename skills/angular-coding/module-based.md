# NgModule Patterns (v13-14)

## Module Structure

```typescript
@NgModule({
  declarations: [
    FeatureComponent,
    FeatureDialogComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    SharedModule,
  ],
  exports: [
    FeatureComponent,
  ],
  providers: [
    FeatureService,
  ],
})
export class FeatureModule {}
```

## Component with Module

```typescript
@Component({
  selector: 'bls-feature',
  templateUrl: './feature.component.html',
  styleUrls: ['./feature.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeatureComponent {}
```

**Note:** No `standalone: true` flag - component belongs to module.

## Lazy Loading

### Route Configuration

```typescript
const routes: Routes = [
  {
    path: 'feature',
    loadChildren: () => import('./feature/feature.module').then(m => m.FeatureModule),
  },
];
```

### Feature Routing Module

```typescript
const routes: Routes = [
  { path: '', component: FeatureComponent },
  { path: 'details/:id', component: FeatureDetailsComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class FeatureRoutingModule {}
```

## Shared Module Pattern

```typescript
@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  declarations: [
    // Shared components, directives, pipes
  ],
  exports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    // Re-export shared components
  ],
})
export class SharedModule {}
```

## Provider Patterns

### Module-level Provider

```typescript
@NgModule({
  providers: [
    FeatureService,
    { provide: API_URL, useValue: environment.apiUrl },
  ],
})
export class FeatureModule {}
```

### Root Provider (Preferred)

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureService {}
```

## v14 Specific: inject() Function

v14 introduced `inject()` as alternative to constructor injection:

```typescript
// v14+ (works in module-based too)
private _http = inject(HttpClient);
private _router = inject(Router);

// v13 (constructor only)
constructor(
  private _http: HttpClient,
  private _router: Router
) {}
```

## v14 Specific: Typed Forms

```typescript
// v14+ Typed FormGroup
form = new FormGroup({
  name: new FormControl('', { nonNullable: true }),
  email: new FormControl('', Validators.required),
  age: new FormControl<number | null>(null),
});

// Access with type safety
const name: string = this.form.controls.name.value;
```

## Migration Notes

- v14 is last version before standalone becomes stable
- Consider migrating to standalone for v15+
- `inject()` function works in both module and standalone
