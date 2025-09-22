"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { TilesRenderer } from "3d-tiles-renderer";

type ThreeTilesViewerProps = {
  tilesetUrl: string;
  lat?: number;
  lon?: number;
  iso?: string;
  solarApiBase?: string;
};

export default function ThreeTilesViewer({
  tilesetUrl,
  lat,
  lon,
  iso,
  solarApiBase = "/api/solpos"
}: ThreeTilesViewerProps) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = container.current;
    if (!el) {
      return;
    }

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(el.clientWidth, el.clientHeight);
    el.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xfafafa);

    const camera = new THREE.PerspectiveCamera(60, el.clientWidth / el.clientHeight, 0.1, 1_000_000_000);
    camera.position.set(1500, 1500, 1500);

    const ambient = new THREE.AmbientLight(0xffffff, 0.2);
    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(1000, 2000, 1000);
    scene.add(ambient, sun);

    const tiles = new TilesRenderer(tilesetUrl);
    tiles.setCamera(camera);
    tiles.setResolutionFromRenderer(camera, renderer);
    scene.add(tiles.group);

    let isDragging = false;
    let prev = { x: 0, y: 0 };

    const handleMouseDown = (event: MouseEvent) => {
      isDragging = true;
      prev = { x: event.clientX, y: event.clientY };
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const handleMouseMove = (event: MouseEvent) => {
      if (!isDragging) {
        return;
      }
      const dx = (event.clientX - prev.x) * 0.005;
      const dy = (event.clientY - prev.y) * 0.005;
      prev = { x: event.clientX, y: event.clientY };
      camera.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), -dx);
      camera.position.y = Math.max(10, camera.position.y + dy * 200);
      camera.lookAt(0, 0, 0);
    };

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      const scale = Math.exp(-event.deltaY * 0.001);
      camera.position.multiplyScalar(scale);
    };

    el.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("mousemove", handleMouseMove);
    el.addEventListener("wheel", handleWheel, { passive: false });

    const handleResize = () => {
      const width = el.clientWidth;
      const height = el.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener("resize", handleResize);

    async function updateSunDirection() {
      if (lat == null || lon == null || !iso) {
        return;
      }

      try {
        const params = new URLSearchParams({ lat: String(lat), lon: String(lon), iso });
        const response = await fetch(`${solarApiBase}?${params.toString()}`);
        const { azimuth_deg: azimuthDeg, elevation_deg: elevationDeg } = await response.json();

        if (typeof azimuthDeg === "number" && typeof elevationDeg === "number") {
          const azimuth = (azimuthDeg * Math.PI) / 180;
          const elevation = (elevationDeg * Math.PI) / 180;
          const radius = 5000;
          const x = radius * Math.cos(elevation) * Math.sin(azimuth);
          const y = radius * Math.sin(elevation);
          const z = radius * Math.cos(elevation) * Math.cos(azimuth);
          sun.position.set(x, y, z);
        }
      } catch (error) {
        console.error("solpos error", error);
      }
    }

    updateSunDirection();

    let animationId = 0;
    const loop = () => {
      animationId = requestAnimationFrame(loop);
      tiles.update();
      renderer.render(scene, camera);
    };
    loop();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("mousemove", handleMouseMove);
      el.removeEventListener("mousedown", handleMouseDown);
      el.removeEventListener("wheel", handleWheel);
      el.replaceChildren();
      tiles.dispose();
      renderer.dispose();
    };
  }, [iso, lat, lon, solarApiBase, tilesetUrl]);

  return <div ref={container} className="viewer ysh-gradient-border" />;
}
