import { notFound } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';

const SWATCHES = [
  'background',
  'foreground',
  'card',
  'primary',
  'primary-foreground',
  'secondary',
  'muted',
  'muted-foreground',
  'accent',
  'destructive',
  'border',
  'ring',
  'sidebar',
  'sidebar-accent',
] as const;

export default function TokensPage() {
  if (process.env.NODE_ENV === 'production') notFound();

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-8">
      <h1 className="font-heading text-2xl font-medium">Design tokens</h1>
      <p className="text-sm text-muted-foreground">
        Visual diff against <code>tuvi-v2/project/fortune-app/globals.css</code>. Light mode only.
      </p>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Colors</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SWATCHES.map((name) => (
            <div key={name} className="flex flex-col gap-1.5">
              <div
                className="h-12 rounded-md border border-border"
                style={{ background: `var(--${name})` }}
              />
              <code className="text-[11px] text-muted-foreground">{name}</code>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Typography</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <div className="font-heading text-2xl">Sans / heading — Tử Vi AI</div>
          <div className="font-mono text-sm">Mono — 14.08.1991 · 06:30</div>
          <div className="text-[10px]">10px chính tinh density (fixed)</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Primitives</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-2">
            <Button>Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Destructive</Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge>Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge variant="destructive">Destructive</Badge>
          </div>
          <Separator />
          <div className="flex flex-col gap-2">
            <Label htmlFor="demo-input">Label</Label>
            <Input id="demo-input" placeholder="Input" />
          </div>
          <Progress value={67} />
          <Skeleton className="h-8 w-full" />
        </CardContent>
      </Card>
    </div>
  );
}
