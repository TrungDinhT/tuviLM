"use client";

import { Drawer as DrawerPrimitive } from "@base-ui/react/drawer";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import styles from "./drawer.module.css";

/** Bottom drawer, composed like shadcn's Base UI Drawer. */
export function Drawer(props: Omit<ComponentProps<typeof DrawerPrimitive.Root>, "swipeDirection">) {
  return <DrawerPrimitive.Root swipeDirection="down" {...props} />;
}
export const DrawerTrigger = DrawerPrimitive.Trigger;
export const DrawerClose = DrawerPrimitive.Close;
export const DrawerPortal = DrawerPrimitive.Portal;

export function DrawerOverlay() {
  return <DrawerPrimitive.Backdrop data-slot="drawer-overlay" className={styles.overlay} />;
}

export function DrawerContent({
  children,
  className,
  ...props
}: Omit<ComponentProps<typeof DrawerPrimitive.Popup>, "className"> & { className?: string }) {
  return (
    <DrawerPortal>
      <DrawerOverlay />
      <DrawerPrimitive.Viewport className={styles.viewport}>
        <DrawerPrimitive.Popup
          data-slot="drawer-content"
          className={cn(styles.popup, className)}
          {...props}
        >
          <div className={styles.handle} aria-hidden="true" />
          {children}
        </DrawerPrimitive.Popup>
      </DrawerPrimitive.Viewport>
    </DrawerPortal>
  );
}

export function DrawerHeader({ className, ...props }: ComponentProps<"div">) {
  return <div data-slot="drawer-header" className={cn(styles.header, className)} {...props} />;
}
export function DrawerFooter({ className, ...props }: ComponentProps<"div">) {
  return <div data-slot="drawer-footer" className={cn(styles.footer, className)} {...props} />;
}
export function DrawerTitle({
  className,
  ...props
}: Omit<ComponentProps<typeof DrawerPrimitive.Title>, "className"> & { className?: string }) {
  return (
    <DrawerPrimitive.Title
      data-slot="drawer-title"
      className={cn(styles.title, className)}
      {...props}
    />
  );
}
export function DrawerDescription({
  className,
  ...props
}: Omit<ComponentProps<typeof DrawerPrimitive.Description>, "className"> & { className?: string }) {
  return (
    <DrawerPrimitive.Description
      data-slot="drawer-description"
      className={cn(styles.description, className)}
      {...props}
    />
  );
}
export function DrawerBody({
  className,
  ...props
}: Omit<ComponentProps<typeof DrawerPrimitive.Content>, "className"> & { className?: string }) {
  return (
    <DrawerPrimitive.Content
      data-slot="drawer-body"
      className={cn(styles.body, className)}
      {...props}
    />
  );
}
