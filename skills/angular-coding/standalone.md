# Standalone Components (v15+)

## Standalone Component

```typescript
@Component({
  standalone: true,
  selector: 'bls-feature',
  templateUrl: './feature.component.html',
  styleUrls: ['./feature.component.scss'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatTableModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeatureComponent {}
```

## Standalone Directive

```typescript
@Directive({
  standalone: true,
  selector: '[blsHighlight]',
})
export class HighlightDirective {}
```

## Standalone Pipe

```typescript
@Pipe({
  standalone: true,
  name: 'blsFormat',
})
export class FormatPipe implements PipeTransform {
  transform(value: string): string {
    return value;
  }
}
```

## Bootstrapping

### main.ts

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
```

### app.config.ts

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideAnimations(),
    // Custom providers
    provideAuth(),
    provideMaterial(),
  ],
};
```

## Lazy Loading

### Route-based Lazy Loading

```typescript
const routes: Routes = [
  {
    path: 'feature',
    loadComponent: () => import('./feature/feature.component')
      .then(m => m.FeatureComponent),
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/routes')
      .then(m => m.ADMIN_ROUTES),
  },
];
```

### routes.ts File Pattern

```typescript
// admin/routes.ts
export const ADMIN_ROUTES: Routes = [
  { path: '', component: AdminDashboardComponent },
  { path: 'users', component: AdminUsersComponent },
  { path: 'settings', component: AdminSettingsComponent },
];
```

## Importing NgModules

Standalone components can still import NgModules:

```typescript
@Component({
  standalone: true,
  imports: [
    // Standalone
    CommonModule,
    ReactiveFormsModule,
    // NgModule-based libraries
    MatButtonModule,
    MatTableModule,
  ],
})
```

## Provider Patterns

### Route-level Providers

```typescript
const routes: Routes = [
  {
    path: 'admin',
    providers: [
      AdminService,
      { provide: ADMIN_CONFIG, useValue: config },
    ],
    children: [...],
  },
];
```

### Environment Injector

```typescript
import { createEnvironmentInjector, EnvironmentInjector } from '@angular/core';

const injector = createEnvironmentInjector(
  [{ provide: FeatureService, useClass: CustomFeatureService }],
  parentInjector
);
```

## Migration from NgModule

1. Add `standalone: true` to component
2. Move `declarations` imports to component `imports`
3. Remove component from module `declarations`
4. Update lazy loading to use `loadComponent`

```typescript
// Before (NgModule)
@NgModule({
  declarations: [FeatureComponent],
  imports: [CommonModule, MatButtonModule],
})
export class FeatureModule {}

// After (Standalone)
@Component({
  standalone: true,
  imports: [CommonModule, MatButtonModule],
})
export class FeatureComponent {}
```
