"""Controlled rosbag2 recording and playback."""

import shutil
import signal
import subprocess
from pathlib import Path
from uuid import uuid4


class RosbagMixin:
    """Manage rosbag2 processes through structured MCP operations."""

    def _init_rosbag_registry(self) -> None:
        """Initialize rosbag recording and playback registries."""
        self._bag_recordings: dict[str, dict[str, object]] = {}
        self._bag_playbacks: dict[str, dict[str, object]] = {}

        self._bag_root = (
            Path(__file__).resolve().parents[4]
            / "bags"
        )
        self._bag_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _ros2_executable(self) -> str:
        """Return the active ROS 2 CLI executable."""
        ros2 = shutil.which("ros2")

        if ros2 is None:
            raise RuntimeError(
                "ros2 executable was not found in PATH."
            )

        return ros2

    def _resolve_bag_name(
        self,
        bag_name: str,
    ) -> Path:
        """Resolve a safe bag name under the managed bag root."""
        normalized_name = self._validate_simple_name(
            bag_name,
            "bag_name",
        )

        return self._bag_root / normalized_name

    @staticmethod
    def _bag_process_snapshot(
        bag_id: str,
        entry: dict[str, object],
        kind: str,
    ) -> dict[str, object]:
        """Return state for a managed rosbag process."""
        process = entry["process"]
        return_code = process.poll()

        return {
            f"{kind}_id": bag_id,
            "bag_path": entry["bag_path"],
            "pid": process.pid,
            "running": return_code is None,
            "return_code": return_code,
        }

    def start_bag_recording(
        self,
        bag_name: str,
        topics: list[str],
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start a rosbag2 recording for explicitly named topics."""
        # # SAFETY:RosbagMixin:start_bag_recording
        self._validate_bag_recording_limit()
        if not topics:
            raise ValueError(
                "At least one topic must be provided."
            )

        normalized_topics = []

        for topic in topics:
            name = str(topic).strip()

            if not name.startswith("/"):
                name = f"/{name}"

            if "\x00" in name or "\n" in name:
                raise ValueError(
                    "Invalid topic name."
                )

            normalized_topics.append(name)

        bag_path = self._resolve_bag_name(
            bag_name
        )

        command = [
            self._ros2_executable(),
            "bag",
            "record",
            *normalized_topics,
            "-o",
            str(bag_path),
        ]

        if dry_run:
            return {
                "dry_run": True,
                "bag_path": str(bag_path),
                "topics": normalized_topics,
            }

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        recording_id = uuid4().hex

        self._bag_recordings[recording_id] = {
            "process": process,
            "bag_path": str(bag_path),
            "topics": normalized_topics,
        }

        result = self._bag_process_snapshot(
            recording_id,
            self._bag_recordings[recording_id],
            "recording",
        )
        result["topics"] = normalized_topics

        return result

    def stop_bag_recording(
        self,
        recording_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop an MCP-owned rosbag recording."""
        normalized_id = recording_id.strip().lower()

        entry = self._bag_recordings.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed bag recording not found: {normalized_id}"
            )

        process = entry["process"]

        if process.poll() is None:
            process.send_signal(signal.SIGINT)

            try:
                process.wait(timeout=timeout_sec)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=timeout_sec)

        result = self._bag_process_snapshot(
            normalized_id,
            entry,
            "recording",
        )
        result["stopped"] = True

        del self._bag_recordings[normalized_id]

        return result

    def get_bag_info(
        self,
        bag_name: str,
    ) -> dict[str, object]:
        """Return rosbag2 metadata using the official ROS 2 bag CLI."""
        bag_path = self._resolve_bag_name(
            bag_name
        )

        if not bag_path.exists():
            raise LookupError(
                f"Managed rosbag not found: {bag_name}"
            )

        result = subprocess.run(
            [
                self._ros2_executable(),
                "bag",
                "info",
                str(bag_path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        return {
            "bag_name": bag_name,
            "bag_path": str(bag_path),
            "return_code": result.returncode,
            "info": result.stdout,
            "error": result.stderr,
        }

    def start_bag_playback(
        self,
        bag_name: str,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Start playback of a managed rosbag."""
        # # SAFETY:RosbagMixin:start_bag_playback
        self._validate_bag_playback_limit()
        bag_path = self._resolve_bag_name(
            bag_name
        )

        if not bag_path.exists():
            raise LookupError(
                f"Managed rosbag not found: {bag_name}"
            )

        command = [
            self._ros2_executable(),
            "bag",
            "play",
            str(bag_path),
        ]

        if dry_run:
            return {
                "dry_run": True,
                "bag_path": str(bag_path),
            }

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        playback_id = uuid4().hex

        self._bag_playbacks[playback_id] = {
            "process": process,
            "bag_path": str(bag_path),
        }

        return self._bag_process_snapshot(
            playback_id,
            self._bag_playbacks[playback_id],
            "playback",
        )

    def stop_bag_playback(
        self,
        playback_id: str,
        timeout_sec: float,
    ) -> dict[str, object]:
        """Stop one MCP-owned rosbag playback."""
        normalized_id = playback_id.strip().lower()

        entry = self._bag_playbacks.get(
            normalized_id
        )

        if entry is None:
            raise LookupError(
                f"Managed bag playback not found: {normalized_id}"
            )

        process = entry["process"]

        if process.poll() is None:
            process.send_signal(signal.SIGINT)

            try:
                process.wait(timeout=timeout_sec)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=timeout_sec)

        result = self._bag_process_snapshot(
            normalized_id,
            entry,
            "playback",
        )
        result["stopped"] = True

        del self._bag_playbacks[normalized_id]

        return result

    def _close_rosbags(self) -> None:
        """Best-effort cleanup of MCP-owned rosbag processes."""
        for recording_id in list(
            self._bag_recordings
        ):
            try:
                self.stop_bag_recording(
                    recording_id,
                    timeout_sec=1.0,
                )
            except Exception:
                pass

        for playback_id in list(
            self._bag_playbacks
        ):
            try:
                self.stop_bag_playback(
                    playback_id,
                    timeout_sec=1.0,
                )
            except Exception:
                pass
